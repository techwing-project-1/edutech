from typing import List, Dict, Any
import json
import uuid
from pydantic import ValidationError
from app.domain.schemas.calendar_agent import CalendarAgentRequest, CalendarAgentResponse, CalendarEvent, EventCategory
from app.domain.schemas.assignment_agent import AssignmentAgentRequest
from app.agents.assignment.manager import AssignmentManager
from app.services.retriever.manager import RetrieverManager
from app.domain.schemas.retriever import RetrieverRequest
from app.services.rag.validator import ContextValidator
from app.services.rag.context_builder import ContextBuilder
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.domain.schemas.llm import LLMRequest
from app.core.exceptions import CalendarAgentException, EmptyContextError
from app.core.logger import logger
import time

class CalendarService:
    def __init__(self):
        self.assignment_manager = AssignmentManager()
        self.retriever = RetrieverManager()
        self.llm_manager = LLMManager()

    async def generate_calendar(self, request: CalendarAgentRequest, query_override: str = None) -> CalendarAgentResponse:
        start_time = time.time()
        try:
            # 1. RAG Retrieval for Syllabus Schedule
            from app.services.rag.query_builder import RAGQueryBuilder
            query = RAGQueryBuilder.build_query(
                request=request,
                query_override=query_override,
                fallback="What are the specific dates, deadlines, schedules, timetable, exams, and milestones in the syllabus?"
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
                raise CalendarAgentValidationError(f"Invalid RetrieverRequest parameters: {str(ve)}")
                
            retriever_res = await self.retriever.search(retriever_req)
            logger.info(f"Retrieved {retriever_res.retrieved_chunk_count} chunks.")
            for idx, chunk in enumerate(retriever_res.chunks):
                logger.info(f"Chunk {idx + 1} | Score: {chunk.score} | Confidence: {chunk.confidence}")
            
            valid_chunks = ContextValidator.validate_context_size(retriever_res.chunks)
            
            if not valid_chunks:
                logger.warning("No valid chunks retrieved for Calendar extraction. Throwing EmptyContextError.")
                raise EmptyContextError("No relevant syllabus content found for calendar generation.")
                
            context_string = ContextBuilder.build_context_string(valid_chunks)

            # 2. Extract Assignments (Optional, gracefully fallback if empty)
            assignments_json = []
            try:
                assignment_req = AssignmentAgentRequest(
                    user_id=request.user_id,
                    department=request.department,
                    semester=request.semester,
                    subject=request.subject,
                    section=request.section
                )
                assignment_res = await self.assignment_manager.extract(assignment_req)
                assignments_json = [a.model_dump() for a in assignment_res.assignments]
            except EmptyContextError:
                logger.info("No assignments found, proceeding with calendar generation based on syllabus only.")
            except Exception as e:
                logger.warning(f"Assignment extraction failed during calendar generation: {e}")

            from app.services.prompts.builder import PromptBuilder
            system_prompt = PromptBuilder.get_strict_rag_system_prompt(
                role="Calendar Scheduler",
                extra_instructions=(
                    "CRITICAL INSTRUCTIONS:\n"
                    "1. You MUST ONLY use the retrieved syllabus context and provided assignments.\n"
                    "2. If dates are not provided in the context, you may estimate relative weekly dates from start of semester, but DO NOT invent fictional syllabus topics.\n"
                    "3. Return ONLY a valid JSON array of event objects matching these keys:\n"
                    "event_id, title, description, start_date (ISO 8601), end_date (ISO 8601), priority, category (ASSIGNMENT, REVISION, EXAM, LAB, PROJECT, REMINDER), color_tag (hex code), recurring (boolean), recurrence_rule (string or null), reminders (array of ints).\n"
                    "No markdown wrapping."
                )
            )
            
            prompt = (
                f"Syllabus Context:\n{context_string}\n\n"
                f"Assignments data:\n{json.dumps(assignments_json, indent=2)}\n\n"
                "Generate the calendar events as a JSON array based ONLY on the above syllabus context and assignments."
            )
            
            llm_request = LLMRequest(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=3000
            )
            
            llm_response = await self.llm_manager.generate_response(llm_request)
            
            # Parse JSON
            raw_text = extract_text(llm_response).strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3]
            
            try:
                events_data = json.loads(raw_text)
                if not isinstance(events_data, list):
                    events_data = [events_data]
            except json.JSONDecodeError:
                events_data = []

            events = []
            stats = {"ASSIGNMENT": 0, "REVISION": 0, "EXAM": 0, "LAB": 0, "PROJECT": 0, "REMINDER": 0, "TOTAL": 0}
            
            # Generate ICS string
            ics_lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CurriculaMind//Calendar Agent//EN"]
            
            for ed in events_data:
                category_str = ed.get("category", "ASSIGNMENT")
                if category_str not in [c.value for c in EventCategory]:
                    category_str = "ASSIGNMENT"
                    
                cat = EventCategory(category_str)
                stats[cat.value] += 1
                stats["TOTAL"] += 1
                
                start_str = ed.get("start_date", "2027-01-01T00:00:00Z")
                end_str = ed.get("end_date", "2027-01-01T01:00:00Z")
                
                event = CalendarEvent(
                    event_id=ed.get("event_id", str(uuid.uuid4())),
                    title=ed.get("title", "Event"),
                    description=ed.get("description", ""),
                    start_date=start_str,
                    end_date=end_str,
                    priority=ed.get("priority", "Normal"),
                    category=cat,
                    color_tag=ed.get("color_tag", "#3788d8"),
                    recurring=ed.get("recurring", False),
                    recurrence_rule=ed.get("recurrence_rule"),
                    reminders=ed.get("reminders", [15])
                )
                events.append(event)
                
                # Basic ICS formatting
                ics_lines.append("BEGIN:VEVENT")
                ics_lines.append(f"UID:{event.event_id}")
                ics_lines.append(f"SUMMARY:{event.title}")
                ics_lines.append(f"DESCRIPTION:{event.description}")
                # Convert ISO string to ICS format (e.g., 20270101T000000Z)
                ics_start = start_str.replace("-", "").replace(":", "").split(".")[0]
                if not ics_start.endswith("Z"): ics_start += "Z"
                ics_end = end_str.replace("-", "").replace(":", "").split(".")[0]
                if not ics_end.endswith("Z"): ics_end += "Z"
                
                ics_lines.append(f"DTSTART:{ics_start}")
                ics_lines.append(f"DTEND:{ics_end}")
                if event.recurrence_rule:
                    ics_lines.append(f"RRULE:{event.recurrence_rule}")
                ics_lines.append("END:VEVENT")

            ics_lines.append("END:VCALENDAR")
            ics_file = "\n".join(ics_lines)
            
            json_events_str = json.dumps([e.model_dump() for e in events])
            
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
            
            return CalendarAgentResponse(
                calendar_id=str(uuid.uuid4()),
                events=events,
                ics_file=ics_file,
                json_events=json_events_str,
                statistics=stats,
                metadata={
                    "provider_used": llm_response.provider_used,
                    "model_used": getattr(llm_response, 'model_name', getattr(llm_response, 'model_used', 'Unknown')),
                    "retriever_time_ms": int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0,
                    "sources": source_attribution
                }
            )

        except EmptyContextError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate calendar: {str(e)}")
            raise CalendarAgentException(f"Generation failed: {str(e)}")
