import json
import uuid
from pydantic import ValidationError
from app.domain.schemas.study_planner import (
    StudyPlannerRequest, StudyPlannerResponse, DailyPlan, WeeklyPlan, StudyIntensity
)
from app.domain.schemas.calendar_agent import CalendarAgentRequest
from app.agents.calendar.manager import CalendarManager
from app.services.retriever.manager import RetrieverManager
from app.domain.schemas.retriever import RetrieverRequest
from app.services.rag.validator import ContextValidator
from app.services.rag.context_builder import ContextBuilder
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.domain.schemas.llm import LLMRequest
from app.core.exceptions import StudyPlannerException, EmptyContextError
from app.core.logger import logger
import time

class StudyPlannerService:
    def __init__(self):
        self.calendar_manager = CalendarManager()
        self.retriever = RetrieverManager()
        self.llm_manager = LLMManager()

    async def generate_plan(self, request: StudyPlannerRequest, query_override: str = None) -> StudyPlannerResponse:
        start_time = time.time()
        try:
            # 1. RAG Retrieval for Syllabus Topics
            from app.services.rag.query_builder import RAGQueryBuilder
            query = RAGQueryBuilder.build_query(
                request=request,
                query_override=query_override,
                fallback="What are the course modules, syllabus topics, chapters, and required readings to study?"
            )
            
            logger.info(f"Final search query: '{query}'")
            
            try:
                retriever_req = RetrieverRequest(
                    query=query,
                    department=request.department,
                    semester=request.semester,
                    subject=request.subject,
                    section=request.section,
                    top_k=10
                )
                logger.debug(f"Constructed RetrieverRequest: {retriever_req.model_dump_json(indent=2)}")
            except ValidationError as ve:
                logger.error(f"RetrieverRequest validation failed: {ve}")
                raise StudyPlannerValidationError(f"Invalid RetrieverRequest parameters: {str(ve)}")
                
            retriever_res = await self.retriever.search(retriever_req)
            logger.info(f"Retrieved {retriever_res.retrieved_chunk_count} chunks.")
            for idx, chunk in enumerate(retriever_res.chunks):
                logger.info(f"Chunk {idx + 1} | Score: {chunk.score} | Confidence: {chunk.confidence}")
                
            valid_chunks = ContextValidator.validate_context_size(retriever_res.chunks)
            
            if not valid_chunks:
                logger.warning("No valid chunks retrieved for StudyPlanner extraction. Throwing EmptyContextError.")
                raise EmptyContextError("No relevant syllabus content found for study planner generation.")
                
            context_string = ContextBuilder.build_context_string(valid_chunks)

            # 2. Extract Calendar Events (Optional, gracefully fallback if empty)
            events_json = ""
            try:
                cal_req = CalendarAgentRequest(
                    user_id=request.user_id,
                    department=request.department,
                    semester=request.semester,
                    subject=request.subject,
                    section=request.section
                )
                cal_res = await self.calendar_manager.generate(cal_req)
                events_json = cal_res.json_events
            except EmptyContextError:
                logger.info("No calendar events found, proceeding with study plan based on syllabus topics only.")
            except Exception as e:
                logger.warning(f"Calendar extraction failed during study plan generation: {e}")
            
            from app.services.prompts.builder import PromptBuilder
            system_prompt = PromptBuilder.get_strict_rag_system_prompt(
                role="Study Planner",
                extra_instructions=(
                    "CRITICAL INSTRUCTIONS:\n"
                    "1. You MUST ONLY use the retrieved syllabus topics context and provided calendar events.\n"
                    "2. Your goal is to map the specific syllabus topics into a structured daily and weekly study plan.\n"
                    "3. Return ONLY a valid JSON object matching the requested schema.\n"
                    "No markdown wrapping."
                )
            )
            
            prompt = (
                f"Syllabus Topics Context:\n{context_string}\n\n"
                f"Calendar Events Data:\n{events_json}\n\n"
                f"Student Preferences:\n"
                f"- Study Hours Per Day: {request.study_hours_per_day}\n"
                f"- Study Intensity: {request.study_intensity.value}\n"
                f"- Preferred Timings: {request.preferred_study_timings}\n\n"
                "Generate the comprehensive study plan based ONLY on the syllabus topics above. Return as a JSON object with these exact keys:\n"
                "daily_plan (array of objects with 'date', 'targets' (array of string), 'hours_allocated'),\n"
                "weekly_plan (array of objects with 'week_number', 'milestones' (array of string)),\n"
                "monthly_plan (array of strings),\n"
                "revision_schedule (array of strings),\n"
                "exam_preparation (array of strings),\n"
                "lab_preparation (array of strings),\n"
                "project_roadmap (array of strings),\n"
                "break_suggestions (array of strings),\n"
                "completion_estimate (string)."
            )
            
            llm_request = LLMRequest(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=4000
            )
            
            llm_response = await self.llm_manager.generate_response(llm_request)
            
            raw_text = extract_text(llm_response).strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3]
                
            try:
                plan_data = json.loads(raw_text)
            except json.JSONDecodeError:
                plan_data = {}

            # Fallbacks and mapping
            daily_plans_raw = plan_data.get("daily_plan", [])
            daily_plans = []
            for dp in daily_plans_raw:
                daily_plans.append(DailyPlan(
                    date=dp.get("date", "Unknown"),
                    targets=dp.get("targets", []),
                    hours_allocated=float(dp.get("hours_allocated", request.study_hours_per_day))
                ))
                
            weekly_plans_raw = plan_data.get("weekly_plan", [])
            weekly_plans = []
            for wp in weekly_plans_raw:
                weekly_plans.append(WeeklyPlan(
                    week_number=wp.get("week_number", 1),
                    milestones=wp.get("milestones", []),
                    daily_plans=[] # Simplification for now or extract if provided
                ))
                
            # Compile Source Metadata
            source_attribution = [
                {
                    "chunk_id": chunk.id,
                    "score": chunk.score,
                    "document_name": getattr(chunk.metadata, 'document_name', 'Unknown') if chunk.metadata else 'Unknown',
                    "page_number": getattr(chunk.metadata, 'page_number', None) if chunk.metadata else None
                }
                for chunk in valid_chunks
            ]
                
            return StudyPlannerResponse(
                planner_id=str(uuid.uuid4()),
                daily_plan=daily_plans,
                weekly_plan=weekly_plans,
                monthly_plan=plan_data.get("monthly_plan", []),
                revision_schedule=plan_data.get("revision_schedule", []),
                exam_preparation=plan_data.get("exam_preparation", []),
                lab_preparation=plan_data.get("lab_preparation", []),
                project_roadmap=plan_data.get("project_roadmap", []),
                study_hours=request.study_hours_per_day,
                break_suggestions=plan_data.get("break_suggestions", ["Take a 5 minute break every 25 minutes"]),
                completion_estimate=plan_data.get("completion_estimate", "End of semester"),
                metadata={
                    "provider_used": llm_response.provider_used,
                    "model_used": getattr(llm_response, 'model_name', getattr(llm_response, 'model_used', 'Unknown')),
                    "retriever_time_ms": int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0, # Assuming we add start_time at top
                    "sources": source_attribution
                }
            )

        except EmptyContextError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate study plan: {str(e)}")
            raise StudyPlannerException(f"Generation failed: {str(e)}")
