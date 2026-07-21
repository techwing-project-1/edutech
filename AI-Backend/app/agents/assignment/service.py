from typing import List, Dict, Any
import json
from app.domain.schemas.assignment_agent import AssignmentAgentRequest, AssignmentAgentResponse, AssignmentItem
from app.services.rag.context_builder import ContextBuilder
from app.services.rag.validator import ContextValidator
from app.services.retriever.manager import RetrieverManager
from app.domain.schemas.retriever import RetrieverRequest
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.domain.schemas.llm import LLMRequest
from app.core.exceptions import AssignmentAgentException, AssignmentAgentValidationError, EmptyContextError
from pydantic import ValidationError
from app.core.logger import logger

class AssignmentExtractionService:
    def __init__(self):
        self.retriever = RetrieverManager()
        self.llm_manager = LLMManager()

    async def extract_assignments(self, request: AssignmentAgentRequest, query_override: str = None) -> AssignmentAgentResponse:
        try:
            from app.services.rag.query_builder import RAGQueryBuilder
            query = RAGQueryBuilder.build_query(
                request=request,
                query_override=query_override,
                fallback="What are the assignments, projects, lab experiments, mini projects, exams, deadlines, and submission dates?"
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
                raise AssignmentAgentValidationError(f"Invalid RetrieverRequest parameters: {str(ve)}")
                
            retriever_res = await self.retriever.search(retriever_req)
            logger.info(f"Retrieved {retriever_res.retrieved_chunk_count} chunks.")
            for idx, chunk in enumerate(retriever_res.chunks):
                logger.info(f"Chunk {idx + 1} | Score: {chunk.score} | Confidence: {chunk.confidence}")
                
            valid_chunks = ContextValidator.validate_context_size(retriever_res.chunks)
            
            if not valid_chunks:
                logger.warning("No valid chunks retrieved for assignment extraction. Throwing EmptyContextError.")
                raise EmptyContextError("No assignment information found in the uploaded syllabus.")
                
            context_string = ContextBuilder.build_context_string(valid_chunks)

            from app.services.prompts.builder import PromptBuilder
            system_prompt = PromptBuilder.get_strict_rag_system_prompt(
                role="Assignment Extractor",
                extra_instructions=(
                    "CRITICAL INSTRUCTIONS:\n"
                    "1. You MUST ONLY use the retrieved syllabus context below.\n"
                    "2. Do NOT generate generic educational content or hallucinate assignments that are not explicitly stated.\n"
                    "3. If information is missing, do not invent it.\n"
                    "4. Return ONLY a valid JSON array matching the requested schema. No markdown wrapping."
                )
            )
            
            prompt = (
                "Extract all assignments from the following context.\n"
                f"Context: {context_string}\n\n"
                "Provide the result as a JSON array of objects. Each object must have these keys:\n"
                "assignment_id (string), title (string), subject (string), due_date (string or null), description (string), priority (string: High/Normal/Low), confidence_score (number 0.0-1.0).\n"
                "If no assignments exist, return an empty array []."
            )
            
            llm_request = LLMRequest(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=2048
            )
            
            llm_response = await self.llm_manager.generate_response(llm_request)
            
            # Parsing JSON from LLM Response
            try:
                raw_text = extract_text(llm_response).strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:-3]
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:-3]
                
                assignments_data = json.loads(raw_text)
                if not isinstance(assignments_data, list):
                    assignments_data = [assignments_data]
            except json.JSONDecodeError:
                assignments_data = [] # Fallback
                
            assignments = []
            for item in assignments_data:
                assignments.append(AssignmentItem(
                    assignment_id=item.get("assignment_id", "ID_UNKN"),
                    title=item.get("title", "Unknown"),
                    subject=item.get("subject", request.subject or "Unknown"),
                    department=request.department,
                    semester=request.semester,
                    section=request.section,
                    due_date=item.get("due_date"),
                    description=item.get("description", ""),
                    priority=item.get("priority", "Normal"),
                    confidence_score=item.get("confidence_score", 0.8)
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
            
            return AssignmentAgentResponse(
                assignments=assignments,
                sources=source_attribution,
                metadata={
                    "provider_used": llm_response.provider_used,
                    "model_used": getattr(llm_response, 'model_name', getattr(llm_response, 'model_used', 'Unknown')),
                    "retriever_time_ms": int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
                }
            )
        except EmptyContextError:
            raise
        except Exception as e:
            logger.error(f"Failed to extract assignments: {str(e)}")
            raise AssignmentAgentException(f"Extraction failed: {str(e)}")
