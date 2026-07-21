import asyncio
import time
from typing import Optional
from app.domain.schemas.llm import LLMRequest, LLMResponse
from app.domain.interfaces.llm_provider import LLMProviderInterface
from app.infrastructure.llm_providers.factory import LLMProviderFactory, LLMProviderType
from app.core.config import settings
from app.core.exceptions import LLMProviderException, RateLimitExceeded, TimeoutError, ProviderUnavailable
from app.core.logger import logger
from app.services.llm.error_mapper import ErrorMapper

class LLMManager:
    """
    Production-grade Orchestrator for LLM interactions.
    Implements a strict failover policy with exactly one attempt per provider.
    """
    def __init__(self):
        self.routing_order = []
        
        # Load primary and secondary from config, default to gemini -> openrouter
        primary = getattr(settings, "PRIMARY_PROVIDER", "gemini")
        secondary = getattr(settings, "SECONDARY_PROVIDER", "openrouter")
        
        for prov_str in [primary, secondary]:
            if prov_str:
                try:
                    prov_type = LLMProviderType(prov_str.strip().lower())
                    prov_instance = LLMProviderFactory.get_provider(prov_type)
                    self.routing_order.append(prov_instance)
                except Exception as e:
                    logger.warning(f"Could not load provider {prov_str}. {e}")

        if not self.routing_order:
            self.routing_order = [LLMProviderFactory.get_provider(LLMProviderType.OPENROUTER)]

        self.timeout = settings.LLM_TIMEOUT

    # check_health removed - Health checking is now handled by ProviderHealthMonitor

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """
        Executes the primary provider.
        Automatically falls back to the secondary provider if the primary fails.
        STRICT MAXIMUM OF 2 API CALLS.
        """
        providers_to_try = list(self.routing_order)
        
        # Override if explicitly requested (only try this one if it's explicitly requested)
        if hasattr(request, "provider_name") and request.provider_name and request.provider_name.lower() != "auto":
            try:
                requested_prov = LLMProviderFactory.get_provider(LLMProviderType(request.provider_name.lower()))
                providers_to_try = [requested_prov]
            except Exception as e:
                logger.warning(f"Could not load requested provider {request.provider_name}, falling back to default routing. {e}")

        last_error = None
        global_start_time = time.time()
        
        for i, provider in enumerate(providers_to_try):
            is_fallback = (i > 0)
            try:
                logger.info(f"Attempting generation with provider ({provider.provider_name})... (Fallback: {is_fallback})")
                
                from app.services.llm.health_monitor import ProviderHealthMonitor
                if not ProviderHealthMonitor.is_healthy(provider.provider_name):
                    logger.warning(f"Provider {provider.provider_name} is marked UNHEALTHY in cache, but attempting anyway...")


                # Exactly one attempt with a strict timeout applied at the orchestration layer
                # Note: Providers ALSO have internal timeouts configured for defense-in-depth.
                response = await asyncio.wait_for(provider.generate(request), timeout=self.timeout)
                response.fallback_used = is_fallback
                
                # Record success metrics
                from app.monitoring.metrics import record_llm_metrics
                total_tokens = getattr(response.usage, "total_tokens", 0) if response.usage else 0
                record_llm_metrics(
                    provider=provider.provider_name,
                    model=response.model_name,
                    latency_ms=response.latency_ms,
                    tokens=total_tokens,
                    is_fallback=is_fallback,
                    success=True
                )
                
                # Log success
                logger.info(f"Provider {provider.provider_name} succeeded. Latency: {response.latency_ms}ms.")
                
                return response
                
            except Exception as e:
                # E was already mapped by the provider, but wait_for might raise asyncio.TimeoutError
                if isinstance(e, asyncio.TimeoutError):
                    e = TimeoutError(f"Manager timeout after {self.timeout}s for {provider.provider_name}")
                    
                logger.warning(f"Provider {provider.provider_name} failed: {type(e).__name__} - {str(e)}. Fallback reason: {str(e)}")
                
                # Record failure metrics
                is_quota_error = isinstance(e, RateLimitExceeded)
                from app.monitoring.metrics import record_llm_metrics
                record_llm_metrics(
                    provider=provider.provider_name,
                    model="unknown",
                    latency_ms=0.0,
                    tokens=0,
                    is_fallback=is_fallback,
                    success=False,
                    is_quota_error=is_quota_error
                )
                last_error = e
                continue

        # If we exit the loop, all providers failed.
        total_latency = int((time.time() - global_start_time) * 1000)
        logger.error(f"Critical: All LLM providers failed to generate a response. Total Latency: {total_latency}ms. Last error: {type(last_error).__name__} - {str(last_error)}")
        
        # Raise the specific last error if it's a domain exception, rather than masking it behind 502
        if last_error:
            raise last_error
        
        raise LLMProviderException("Critical: All LLM providers failed to generate a response.", status_code=502)

    async def generate_response_stream(self, request: LLMRequest):
        """
        Executes the primary provider in streaming mode.
        Automatically falls back to the secondary provider if the primary fails at initialization.
        STRICT MAXIMUM OF 2 API CALLS.
        """
        providers_to_try = list(self.routing_order)
        
        if hasattr(request, "provider_name") and request.provider_name and request.provider_name.lower() != "auto":
            try:
                requested_prov = LLMProviderFactory.get_provider(LLMProviderType(request.provider_name.lower()))
                providers_to_try = [requested_prov]
            except Exception as e:
                logger.warning(f"Could not load requested provider {request.provider_name}, falling back to default routing. {e}")

        last_error = None
        global_start_time = time.time()
        
        for i, provider in enumerate(providers_to_try):
            is_fallback = (i > 0)
            try:
                logger.info(f"Attempting stream with provider ({provider.provider_name})... (Fallback: {is_fallback})")
                
                from app.services.llm.health_monitor import ProviderHealthMonitor
                if not ProviderHealthMonitor.is_healthy(provider.provider_name):
                    logger.warning(f"Provider {provider.provider_name} is marked UNHEALTHY in cache, but attempting stream anyway...")


                # Get generator with orchestration timeout on the connection phase
                generator = provider.generate_stream(request)
                
                # Fetch first chunk to trigger any immediate initialization errors
                first_chunk = await asyncio.wait_for(generator.__anext__(), timeout=self.timeout)
                yield first_chunk
                
                async for chunk in generator:
                    yield chunk
                
                # If we made it here without exception, stream succeeded
                latency_ms = (time.time() - global_start_time) * 1000.0
                from app.monitoring.metrics import record_llm_metrics
                record_llm_metrics(
                    provider=provider.provider_name,
                    model="unknown",
                    latency_ms=latency_ms,
                    tokens=0,
                    is_fallback=is_fallback,
                    success=True
                )
                
                logger.info(f"Provider {provider.provider_name} stream succeeded.")
                return
                    
            except Exception as e:
                if isinstance(e, StopAsyncIteration):
                    logger.warning(f"Provider {provider.provider_name} yielded no stream data.")
                    e = LLMProviderException("Stream yielded no data.")
                elif isinstance(e, asyncio.TimeoutError):
                    e = TimeoutError(f"Manager stream timeout after {self.timeout}s for {provider.provider_name}")
                
                logger.warning(f"Provider {provider.provider_name} stream failed: {type(e).__name__} - {str(e)}. Fallback reason: {str(e)}")
                    
                is_quota_error = isinstance(e, RateLimitExceeded)
                from app.monitoring.metrics import record_llm_metrics
                record_llm_metrics(
                    provider=provider.provider_name,
                    model="unknown",
                    latency_ms=0.0,
                    tokens=0,
                    is_fallback=is_fallback,
                    success=False,
                    is_quota_error=is_quota_error
                )
                last_error = e
                continue

        total_latency = int((time.time() - global_start_time) * 1000)
        logger.error(f"Critical: All LLM providers failed to stream a response. Total Latency: {total_latency}ms. Last error: {type(last_error).__name__} - {str(last_error)}")
        
        if last_error:
            raise last_error
            
        raise LLMProviderException("Critical: All LLM providers failed to stream a response.", status_code=502)
