import asyncio
import time
from typing import Dict
from app.core.logger import logger
from app.infrastructure.llm_providers.factory import LLMProviderFactory, LLMProviderType
from app.core.config import settings

class ProviderHealthMonitor:
    """
    Background health monitor for LLM providers.
    Periodically checks provider health without blocking runtime execution.
    """
    _status_cache: Dict[str, bool] = {}
    _running = False

    @classmethod
    async def _check_all_providers(cls):
        providers = [
            LLMProviderFactory.get_provider(LLMProviderType.GEMINI),
            LLMProviderFactory.get_provider(LLMProviderType.OPENROUTER)
        ]
        
        for provider in providers:
            logger.info(f"Checking health for provider: {provider.provider_name}")
            
            # Log initialization / key status
            api_key_loaded = bool(getattr(provider, 'api_key', None))
            logger.info(f"Loaded API keys for {provider.provider_name}: {'YES' if api_key_loaded else 'NO'}")
            
            start_time = time.time()
            try:
                is_healthy = await asyncio.wait_for(provider.health_check(), timeout=10.0)
            except Exception as e:
                logger.warning(f"Health check execution failed for {provider.provider_name}: {e}")
                is_healthy = False
                
            latency_ms = int((time.time() - start_time) * 1000)
            
            cls._status_cache[provider.provider_name] = is_healthy
            
            status_str = "HEALTHY" if is_healthy else "UNHEALTHY"
            logger.info(f"Health check status [{provider.provider_name}]: {status_str} (Latency: {latency_ms}ms)")

    @classmethod
    async def _monitor_loop(cls):
        while cls._running:
            try:
                await cls._check_all_providers()
            except Exception as e:
                logger.error(f"Error in ProviderHealthMonitor loop: {e}")
                
            # Sleep for 5 minutes
            await asyncio.sleep(300)

    @classmethod
    def start_background_checks(cls):
        if not cls._running:
            logger.info("Starting ProviderHealthMonitor background task...")
            cls._running = True
            asyncio.create_task(cls._monitor_loop())

    @classmethod
    def stop_background_checks(cls):
        cls._running = False

    @classmethod
    def is_healthy(cls, provider_name: str) -> bool:
        """
        Returns the cached health status of the provider.
        Defaults to True if unknown (optimistic attempt).
        """
        return cls._status_cache.get(provider_name, True)
