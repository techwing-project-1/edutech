import time
from app.domain.schemas.rag import RAGRequest, RAGResponse
from app.services.retriever.manager import RetrieverManager
from app.domain.schemas.retriever import RetrieverRequest
from app.services.rag.validator import ContextValidator
from app.services.rag.context_builder import ContextBuilder
from app.services.rag.prompt_generator import PromptContextGenerator
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.core.exceptions import RAGException
from app.core.logger import logger
from pydantic import ValidationError

class RAGService:
    """
    Core execution logic for the Retrieval Augmented Generation workflow.
    """
    
    def __init__(self):
        self.retriever = RetrieverManager()
        self.llm_manager = LLMManager()
        
    async def execute_query(self, request: RAGRequest) -> RAGResponse:
        start_time = time.time()
        logger.info(f"RAG Service executing query: '{request.query}'")
        
        try:
            # 1. Retrieve Context
            try:
                retriever_req = RetrieverRequest(
                    query=request.query,
                    document_id=request.document_id,
                    department=request.department,
                    semester=request.semester,
                    subject=request.subject,
                    section=request.section,
                    top_k=request.top_k
                )
            except ValidationError as ve:
                logger.error(f"RetrieverRequest validation failed: {ve}")
                raise RAGException(f"Invalid parameters for RAG retrieval: {str(ve)}")
            
            # Note: Embedding, Similarity Search, Thresholding, and Dedup happen inside RetrieverManager
            retriever_res = await self.retriever.search(retriever_req)
            
            # 2. Validate Context Size (prevent exceeding token limits)
            valid_chunks = ContextValidator.validate_context_size(retriever_res.chunks)
            # Diagnostic Logs
            logger.info("--- RAG DIAGNOSTICS ---")
            logger.info(f"Retrieved Chunk Count (Pre-validation): {len(retriever_res.chunks)}")
            logger.info(f"Valid Chunk Count (Post-validation): {len(valid_chunks)}")
            for idx, c in enumerate(valid_chunks):
                logger.info(f"Chunk {idx + 1} | ID: {c.id} | Score: {c.score} | Text[:50]: {c.text[:50].replace(chr(10), ' ')}...")
                logger.info(f"Metadata: {c.metadata}")
            
            # Hallucination Prevention: Bypass LLM if no chunks retrieved
            if not valid_chunks:
                logger.warning("No context chunks retrieved or all filtered. Returning bypass message.")
                return RAGResponse(
                    answer="No relevant information was found in the uploaded document related to your question.",
                    sources=[],
                    retrieved_chunks=0,
                    llm_provider="None",
                    model="None",
                    success=False,
                    latency_ms=int((time.time() - start_time) * 1000),
                    average_similarity=0.0
                )
                
            # Calculate Confidence Metrics
            avg_sim = sum(c.score for c in valid_chunks) / len(valid_chunks)
            # Confidence is scaled based on top-1 and avg similarity (simplistic heuristic)
            confidence_float = (valid_chunks[0].score * 0.5) + (avg_sim * 0.3) + 0.2
            
            if confidence_float >= 0.80:
                confidence_str = "HIGH"
            elif confidence_float >= 0.60:
                confidence_str = "MEDIUM"
            else:
                confidence_str = "LOW"
                
            logger.info(f"Confidence Metric: {confidence_str} | Score: {confidence_float:.3f} (Avg Similarity: {avg_sim:.3f})")
            
            # 3. Build Context String
            context_string = ContextBuilder.build_context_string(valid_chunks)
            logger.debug(f"Constructed Context String Length: {len(context_string)} chars")
            
            # 4. Generate Prompt Request (Integrates Prompt Layer)
            llm_request = PromptContextGenerator.generate_llm_request(
                question=request.query, 
                context_string=context_string
            )
            logger.info(f"Prepared LLMRequest | System Prompt Length: {len(llm_request.system_prompt or '')} | User Prompt Length: {len(llm_request.prompt)}")
            
            # 5. Execute LLM Call (Integrates Provider Layer with automatic Fallback to OpenRouter)
            llm_start_time = time.time()
            llm_response = await self.llm_manager.generate_response(llm_request)
            llm_latency = int((time.time() - llm_start_time) * 1000)
            logger.info(f"LLM generation successful | Provider: {llm_response.provider_used} | Model: {llm_response.model_name} | Latency: {llm_latency}ms")
            
            # 6. Construct Final RAG Response
            latency = int((time.time() - start_time) * 1000)
            logger.info(f"--- RAG PIPELINE COMPLETE | Latency: {latency}ms ---")
            
            from app.domain.schemas.rag import RAGSource
            formatted_sources = []
            for c in valid_chunks:
                doc_name = getattr(c.metadata, 'document_name', None) or c.document_name or "Unknown"
                page_num = getattr(c.metadata, 'page_number', None) or c.page or 1
                formatted_sources.append(RAGSource(
                    document_name=doc_name,
                    page_number=page_num,
                    chunk_id=c.id,
                    similarity_score=round(c.score, 4),
                    confidence=confidence_str
                ))
            
            return RAGResponse(
                answer=extract_text(llm_response),
                sources=formatted_sources,
                retrieved_chunks=len(valid_chunks),
                llm_provider=llm_response.provider_used or "Unknown",
                model=llm_response.model_name or "Unknown",
                success=True,
                latency_ms=latency,
                average_similarity=round(avg_sim, 3)
            )
            
        except Exception as e:
            logger.error(f"RAG execution failed: {str(e)}")
            raise RAGException(f"Failed to generate answer: {str(e)}")
