import time
import json
import uuid
import asyncio
from typing import AsyncGenerator
from fastapi import HTTPException
from app.core.logger import logger
from app.core.config import settings
from app.domain.schemas.general_ai import GeneralAIRequest, GeneralAIResponse
from app.core.exceptions import GeneralAIException, PromptInjectionDetected
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.services.prompts.builder import PromptBuilder
from app.services.prompts.manager import PromptManager
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.repositories.conversation_repository import ConversationRepository
from app.services.security.moderation import ModerationService
from app.services.general_ai.validator import GeneralAIValidator
from app.monitoring.metrics import record_llm_metrics
from app.services.general_ai.context_manager import ContextManager
from app.services.general_ai.semantic_cache import SemanticCacheService
from app.services.general_ai.intent_classifier import QueryClassifier

class GeneralAIService:
    """
    Core business logic for the General AI Chat API.
    Orchestrates validation, db context, prompt compilation, caching, and model execution.
    """
    
    def __init__(self):
        self.llm_manager = LLMManager()
        self.context_manager = ContextManager()
        self.query_classifier = QueryClassifier()

    async def _get_or_create_conversation(self, repo: ConversationRepository, request: GeneralAIRequest):
        # Priority 1: Resume by explicit conversation_id supplied by client
        if request.conversation_id:
            conv = await repo.get_conversation(request.conversation_id)
            if conv:
                logger.info(f"[GeneralAI] Resuming existing conversation id={conv.id} (matched conversation_id from request)")
                return conv
            else:
                logger.warning(f"[GeneralAI] conversation_id={request.conversation_id} not found in DB — creating new conversation")

        # Priority 2: Resume by session_id (last active conversation for this session)
        if request.session_id:
            conv = await repo.get_conversation_by_session(request.session_id)
            if conv:
                logger.info(f"[GeneralAI] Resuming conversation id={conv.id} matched by session_id={request.session_id}")
                return conv

        # Priority 3: Create a fresh conversation
        conv = await repo.create_conversation(session_id=request.session_id)
        logger.info(f"[GeneralAI] Created new conversation id={conv.id}")
        return conv
        
    def _format_history(self, messages: list) -> str:
        if not messages:
            return ""
        # Convert DB models or dicts to strings
        formatted = []
        for msg in messages:
            if hasattr(msg, "role"):
                formatted.append(f"{msg.role}: {msg.content}")
            else:
                formatted.append(f"{msg.get('role')}: {msg.get('content')}")
        return "\n".join(formatted)

    async def execute_chat(self, request: GeneralAIRequest) -> GeneralAIResponse:
        start_time = time.time()
        
        logger.info(
            f"[GeneralAI] Chat received — query={request.query[:80]!r} "
            f"session_id={request.session_id} conversation_id={request.conversation_id} "
            f"provider={request.provider_name} model={request.model_name}"
        )
        
        try:
            # 1. Validate & Moderate
            GeneralAIValidator.validate_request(request)
            ModerationService.check_for_injection(request.query)
            
            conversation = None
            repo = None
            db_session = None

            # 2. Parallel Processing (Cache Check + Intent Classification + DB Init)
            async def get_classification():
                return await self.query_classifier.classify(request.query)
            
            async def init_db_and_context():
                conv = None
                hist = []
                r = None
                if AsyncSessionLocal:
                    db_session_local = AsyncSessionLocal()
                    r = ConversationRepository(db_session_local)
                    conv = await self._get_or_create_conversation(r, request)
                    
                    is_new_conversation = (getattr(conv, "messages", None) is not None and len(conv.messages) == 0)
                    user_msg = await r.add_message(conv.id, "user", request.query)
                    logger.info(f"[GeneralAI] User message saved id={user_msg.id} conversation_id={conv.id}")
                    
                    if is_new_conversation and conv:
                        asyncio.create_task(self.context_manager.generate_auto_title(conv.id, request.query))
                    
                    if conv:
                        hist = self.context_manager.trim_history(conv.messages[:-1] if conv.messages else [])
                        self.context_manager.trigger_summarization(conv.id, conv.messages[:-1] if conv.messages else [])
                    return db_session_local, r, conv, hist
                else:
                    logger.warning("[GeneralAI] Database not configured — persistence DISABLED")
                    return None, None, None, self.context_manager.trim_history(request.history or [])
            
            # 2. Synchronous Context & DB Initialization
            # We strictly initialize the database and save the user message BEFORE hitting the LLM provider.
            db_session, repo, conversation, history_list = await init_db_and_context()
            
            # 3. Intent Classification (Now instantaneous and local)
            classification = await get_classification()
            
            # 4. Semantic Cache Check
            cached_res = SemanticCacheService.get(request.query)

            if cached_res:
                llm_response = cached_res
                is_cached = True
            else:
                is_cached = False
                
                # 3. Format History
                formatted_history = self._format_history(history_list)
                
                # 4. Generate Prompt
                llm_request = PromptManager.create_llm_request(
                    system_template_name="general_ai_system_v1",
                    user_template_name="general_ai_user_v1",
                    system_kwargs={},
                    user_kwargs={"user_query": request.query, "history": formatted_history},
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    provider_name=request.provider_name,
                    model_name=request.model_name
                )
                
                logger.info("Prompt generation complete.", extra={"extra_info": {"prompt_length": len(llm_request.prompt)}})
                
                # 5. Execute LLM Call
                llm_response = await self.llm_manager.generate_response(llm_request)
                
                # 6. Save to Cache
                # We can't await a normal def, SemanticCacheService is sync so thread it or just run it
                SemanticCacheService.set(request.query, llm_response)
                
            filtered_output = ModerationService.filter_output(extract_text(llm_response))
            
            latency = int((time.time() - start_time) * 1000)
            is_fallback = llm_response.fallback_used
            
            # 5. Save AI response to DB
            response_id = str(uuid.uuid4())
            if repo and conversation:
                metadata = {
                    "model_used": llm_response.model_name,
                    "latency_ms": latency,
                    "token_usage": llm_response.usage.model_dump() if hasattr(llm_response.usage, "model_dump") else llm_response.usage,
                    "fallback_used": is_fallback
                }
                
                total_tokens = llm_response.usage.total_tokens if hasattr(llm_response.usage, "total_tokens") else 0
                
                ai_msg = await repo.add_message(
                    conversation.id, "assistant", filtered_output,
                    provider=llm_response.provider_used,
                    message_metadata=metadata,
                    model_name=llm_response.model_name,
                    prompt_tokens=llm_response.usage.prompt_tokens if hasattr(llm_response.usage, "prompt_tokens") else None,
                    completion_tokens=llm_response.usage.completion_tokens if hasattr(llm_response.usage, "completion_tokens") else None,
                    total_tokens=total_tokens,
                    latency_ms=latency,
                    temperature=request.temperature,
                    response_type=classification["response_type"],
                    language=classification["language"],
                    history_used=len(history_list) > 0,
                    cached=is_cached,
                    processing_time=latency,
                    confidence=0.95
                )
                response_id = ai_msg.id
                logger.info(
                    f"[GeneralAI] Conversation persisted — conversation_id={conversation.id} "
                    f"assistant_message_id={ai_msg.id} provider={llm_response.provider_used} "
                    f"model={llm_response.model_name} latency_ms={latency}"
                )
            
            # 6. Metrics and Logging
            total_tokens = llm_response.usage.total_tokens if hasattr(llm_response.usage, "total_tokens") else 0
            
            record_llm_metrics(
                provider=llm_response.provider_used,
                model=llm_response.model_name,
                latency_ms=latency,
                tokens=total_tokens,
                is_fallback=is_fallback
            )
            
            logger.info(
                "LLM execution complete.",
                extra={
                    "extra_info": {
                        "provider_selected": llm_response.provider_used,
                        "model_name": llm_response.model_name,
                        "latency_ms": latency,
                        "prompt_tokens": llm_response.usage.prompt_tokens if hasattr(llm_response.usage, "prompt_tokens") else 0,
                        "completion_tokens": llm_response.usage.completion_tokens if hasattr(llm_response.usage, "completion_tokens") else 0,
                        "total_tokens": total_tokens,
                        "fallback_used": is_fallback,
                        "conversation_save_status": "SUCCESS" if conversation else "SKIPPED",
                        "assistant_save_status": "SUCCESS" if repo else "SKIPPED",
                        "request_id": request.session_id,  # Or standard req ID
                        "conversation_id": conversation.id if conversation else None
                    }
                }
            )

            conversation_id_out = conversation.id if conversation else None
            logger.info(f"[GeneralAI] Response ready — conversation_id={conversation_id_out} response_id={response_id}")
                
            return GeneralAIResponse(
                answer=filtered_output,
                session_id=request.session_id,
                conversation_id=conversation_id_out,
                message_id=response_id,
                response_id=response_id,
                provider_used=llm_response.provider_used,
                model_name=llm_response.model_name,
                fallback_used=is_fallback,
                latency_ms=latency,
                usage=llm_response.usage,
                response_type=classification["response_type"],
                language=classification["language"],
                history_used=len(history_list) > 0,
                cached=is_cached,
                processing_time=latency,
                confidence=0.95
            )
            
        except PromptInjectionDetected as e:
            e.status_code = 403
            e.error_code = "PROMPT_INJECTION"
            raise e
        except Exception as e:
            if 'db_session' in locals() and db_session:
                await db_session.rollback()
            logger.error(f"General AI execution failed: {str(e)}", exc_info=True)
            # If it's already a DomainException, re-raise it
            from app.core.exceptions import DomainException
            if isinstance(e, DomainException):
                raise e
            raise GeneralAIException(f"Failed to generate answer: {str(e)}")
        finally:
            if 'db_session' in locals() and db_session:
                await db_session.close()

    async def execute_chat_stream(self, request: GeneralAIRequest) -> AsyncGenerator[str, None]:
        """
        Streaming endpoint implementation.
        Yields SSE formatted strings natively from the LLM provider.
        """
        start_time = time.time()
        # 1. Validate & Moderate
        GeneralAIValidator.validate_request(request)
        ModerationService.check_for_injection(request.query)
        
        conversation = None
        repo = None
        db_session = None
        
        try:
            async def get_classification():
                return await self.query_classifier.classify(request.query)
            
            async def init_db_and_context():
                conv = None
                hist = []
                r = None
                if AsyncSessionLocal:
                    db_session_local = AsyncSessionLocal()
                    r = ConversationRepository(db_session_local)
                    conv = await self._get_or_create_conversation(r, request)
                    
                    is_new_conversation = (getattr(conv, "messages", None) is not None and len(conv.messages) == 0)
                    await r.add_message(conv.id, "user", request.query)
                    
                    if is_new_conversation and conv:
                        asyncio.create_task(self.context_manager.generate_auto_title(conv.id, request.query))
                    
                    if conv:
                        hist = self.context_manager.trim_history(conv.messages[:-1] if conv.messages else [])
                        self.context_manager.trigger_summarization(conv.id, conv.messages[:-1] if conv.messages else [])
                    return db_session_local, r, conv, hist
                else:
                    return None, None, None, self.context_manager.trim_history(request.history or [])
            
            # Execute in parallel to save latency
            classification, (db_session, repo, conversation, history_list) = await asyncio.gather(
                get_classification(),
                init_db_and_context()
            )
            
            formatted_history = self._format_history(history_list)
            
            llm_request = PromptManager.create_llm_request(
                system_template_name="general_ai_system_v1",
                user_template_name="general_ai_user_v1",
                system_kwargs={},
                user_kwargs={"user_query": request.query, "history": formatted_history},
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                provider_name=request.provider_name,
                model_name=request.model_name
            )
            
            response_id = str(uuid.uuid4())
            accumulated_answer = ""
            
            # Start stream
            generator = self.llm_manager.generate_response_stream(llm_request)
            
            async for chunk in generator:
                if chunk:
                    extracted_chunk = extract_text(chunk)
                    accumulated_answer += extracted_chunk
                    sse_chunk = {
                        "id": response_id,
                        "choices": [{"delta": {"content": extracted_chunk}}]
                    }
                    yield f"data: {json.dumps(sse_chunk)}\n\n"
                    
            # After stream completes, filter and save
            filtered_output = ModerationService.filter_output(accumulated_answer)
            latency = int((time.time() - start_time) * 1000)
            
            if repo and conversation:
                metadata = {
                    "model_used": llm_request.model_name or "stream-model",
                    "latency_ms": latency,
                    "fallback_used": False
                }
                await repo.add_message(
                    conversation.id, "assistant", filtered_output,
                    provider=llm_request.provider_name or "stream-provider",
                    message_metadata=metadata,
                    model_name=llm_request.model_name,
                    latency_ms=latency,
                    temperature=request.temperature,
                    response_type=classification["response_type"],
                    language=classification["language"],
                    history_used=len(history_list) > 0,
                    cached=False,
                    processing_time=latency,
                    confidence=0.95
                )
                
            # Send final stop chunk
            final_chunk = {
                "id": response_id,
                "choices": [{"delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"
            
        except PromptInjectionDetected as e:
            e.status_code = 403
            e.error_code = "PROMPT_INJECTION"
            raise e
        except Exception as e:
            logger.error(f"Stream error: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            if db_session:
                await db_session.close()
