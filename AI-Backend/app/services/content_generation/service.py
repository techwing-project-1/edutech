import time
from typing import Dict, Any
import uuid

from app.domain.schemas.content_generation import ContentGenerationRequest, ContentGenerationResponse, OutputFormat
from app.services.content_generation.validator import GeneratorValidator
from app.services.content_generation.factory import GeneratorFactory
from app.services.retriever.manager import RetrieverManager
from app.domain.schemas.retriever import RetrieverRequest
from app.services.rag.validator import ContextValidator
from app.services.rag.context_builder import ContextBuilder
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.core.exceptions import (
    ContentGenerationError, EmptyContextError, ProviderError, ContentValidationError, LLMReturnedInvalidJSON
)
from app.core.logger import logger
from pydantic import ValidationError

class ContentGenerationService:
    """
    Core execution logic for the Content Generation Engine.
    Coordinates RAG Retrieval, Prompt Building, and LLM Execution.
    """
    
    def __init__(self):
        self.retriever = RetrieverManager()
        self.llm_manager = LLMManager()

    async def generate(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        logger.info(f"[{request_id}] ContentGenerationService generating '{request.mode}' for topic: '{request.topic}'")
        
        try:
            # 1. Request Validation
            GeneratorValidator.validate_request(request)

            # 2. Retrieve Context via RAG Layer
            # We map the topic to the retriever's expected 'query' field
            try:
                retriever_req = RetrieverRequest(
                    query=request.topic,
                    document_id=request.document_id,
                    department=request.department,
                    semester=request.semester,
                    subject=request.subject,
                    section=request.section,
                    top_k=5 # Default top_k context
                )
            except ValidationError as ve:
                logger.error(f"[{request_id}] RetrieverRequest validation failed: {ve}")
                raise ContentValidationError(f"Invalid RetrieverRequest parameters: {str(ve)}")
            
            # Fetch and build context
            ret_start = time.time()
            retriever_res = await self.retriever.search(retriever_req)
            ret_time = int((time.time() - ret_start) * 1000)
            logger.info(f"[{request_id}] Retriever Time: {ret_time}ms | Chunks: {retriever_res.retrieved_chunk_count}")

            valid_chunks = ContextValidator.validate_context_size(retriever_res.chunks)
            if not valid_chunks:
                logger.warning(f"[{request_id}] No valid context chunks found for topic: {request.topic}")
                raise EmptyContextError("No relevant context found.")

            context_string = ContextBuilder.build_context_string(valid_chunks)

            # 3. Instantiate Generator Strategy via Factory
            # ENFORCE STRICT RAG: Clamp creativity to 0.1 max to eliminate hallucination risks for document-grounded tasks.
            request.creativity = min(request.creativity, 0.1)
            
            generator = GeneratorFactory.create_generator(request.mode)

            # 4. Generate Prompt Request (Integrates Prompt Layer internally via the strategy)
            llm_request = generator.build_prompt(request, context_string)

            # Debug Logging
            context_preview = context_string[:200].replace('\n', ' ') + '...' if len(context_string) > 200 else context_string
            logger.info(f"[{request_id}] Retrieved chunk count: {len(valid_chunks)}")
            logger.info(f"[{request_id}] Context length (chars): {len(context_string)}")
            logger.info(f"[{request_id}] Context preview: {context_preview}")
            logger.info(f"[{request_id}] Prompt length (chars): {len(llm_request.prompt)}")

            # 5. Execute LLM Call (Integrates Provider Layer with automatic Fallback to OpenRouter)
            llm_start = time.time()
            llm_response = await self.llm_manager.generate_response(llm_request)
            llm_time = int((time.time() - llm_start) * 1000)
            
            provider_used = getattr(llm_response, 'provider_used', getattr(llm_response, 'provider_name', 'Unknown'))
            model_used = getattr(llm_response, 'model_name', getattr(llm_response, 'model_used', 'Unknown'))
            
            logger.info(f"[{request_id}] LLM Time: {llm_time}ms | Provider: {provider_used} | Model: {model_used}")

            # 6. Validate Output
            answer = extract_text(llm_response)
            if not answer or not answer.strip():
                raise ProviderError(f"LLM Provider {provider_used} returned an empty response.")
                
            answer = self._sanitize_response(answer, request.output_format)
            
            # Prevent JSON decoder from failing on the strict anti-hallucination fallback text
            if "No relevant information was found" in answer:
                raise EmptyContextError("No relevant context found.")
                
            GeneratorValidator.validate_output(answer, request)
            
            # Grounding Validation (Hallucination check)
            # Skip grounding validation for JSON modes unless we extract text, 
            # for now we'll rely on LLM strictness for JSON or parse it.
            # But the user asked for Grounding Score on all generated text.
            from app.services.rag.grounding_validator import GroundingValidator
            # Validate grounding against retrieved chunks
            # A low threshold because JSON outputs have schema overhead
            GroundingValidator.validate_grounding(answer, valid_chunks, threshold=0.10)

            # 7. Construct Final Response
            total_time = int((time.time() - start_time) * 1000)
            logger.info(f"[{request_id}] --- Content Generation Complete | Total Time: {total_time}ms ---")
            
            # Map chunk sources for traceability
            sources = []
            for chunk in valid_chunks:
                source_meta = {
                    "document_id": getattr(chunk.metadata, 'document_id', None),
                    "chunk_id": chunk.id,
                    "metadata": chunk.metadata.model_dump() if hasattr(chunk.metadata, 'model_dump') else {}
                }
                sources.append(source_meta)

            return ContentGenerationResponse(
                content=answer,
                mode=request.mode,
                format=request.output_format,
                language=request.language,
                sources=sources,
                metadata={
                    "provider_used": provider_used,
                    "model_used": model_used,
                    "retriever_time_ms": ret_time,
                    "llm_time_ms": llm_time,
                    "total_time_ms": total_time,
                    "request_id": request_id
                }
            )

        except EmptyContextError as e:
            # Re-raise to be handled by the route
            raise e
        except LLMReturnedInvalidJSON as e:
            logger.error(f"[{request_id}] Content Generation execution failed: LLMReturnedInvalidJSON: {str(e)}")
            raise e
        except ProviderError as e:
            logger.error(f"[{request_id}] LLM Provider Failed: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"[{request_id}] Content Generation execution failed: {str(e)}")
            raise ContentGenerationError(f"Failed to generate content: {str(e)}")

    def _sanitize_response(self, text: str, output_format: OutputFormat) -> str:
        """
        Actively strip unwanted conversational prefixes that LLMs might inject 
        despite strict prompt engineering. If output_format is JSON, robustly extract the JSON block.
        """
        import re
        
        # If the expected format is JSON, extract ONLY the JSON block by finding outer brackets.
        # This bypasses the need to manually strip conversational strings.
        if output_format == OutputFormat.JSON:
            logger.info("====================\nRAW LLM RESPONSE\n====================\n" + text)
            
            start_idx = -1
            end_idx = -1
            
            # Find first array or object start
            for i, char in enumerate(text):
                if char in ('[', '{'):
                    start_idx = i
                    break
                    
            if start_idx != -1:
                # Find last matching bracket
                expected_end = ']' if text[start_idx] == '[' else '}'
                for i in range(len(text) - 1, -1, -1):
                    if text[i] == expected_end:
                        end_idx = i
                        break
                        
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                extracted = text[start_idx:end_idx+1]
                logger.info("====================\nEXTRACTED JSON RESPONSE\n====================\n" + extracted)
                return extracted
            
            logger.warning("Failed to extract JSON array/object from response. Returning original text.")
            
            # If we were looking for JSON and couldn't find any bounds, the response is hallucinated plain text.
            # We explicitly raise LLMReturnedInvalidJSON so it gets caught properly and retried or errored out.
            logger.error(f"RAW PROVIDER RESPONSE ON SANITIZE FAIL:\n{text}")
            raise LLMReturnedInvalidJSON("Generated content contains no JSON arrays or objects.")
            
        # Phrases to strictly remove for Markdown/Plain text
        unwanted_prefixes = [
            r"^(here is the .*?\n)",
            r"^(here are the .*?\n)",
            r"^(based on the .*?\n)",
            r"^(according to the .*?\n)",
            r"^(based on context.*?\n)",
            r"^(sure,? here .*?\n)",
            r"^(certainly,? .*?\n)",
            r"^(i hope this helps.*?\n)"
        ]
        
        cleaned = text.strip()
        for pattern in unwanted_prefixes:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
            
        return cleaned
