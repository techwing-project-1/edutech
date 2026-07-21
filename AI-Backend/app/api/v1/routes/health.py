from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

from sqlalchemy import text
from app.infrastructure.database.session import AsyncSessionLocal
import asyncio

async def check_database() -> str:
    if AsyncSessionLocal is None:
        return "unconfigured"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_llm_providers() -> str:
    try:
        from app.infrastructure.llm_providers.factory import LLMProviderFactory, LLMProviderType
        prov_type = LLMProviderType(settings.PRIMARY_PROVIDER)
        provider = LLMProviderFactory.get_provider(prov_type)
        return "healthy" if await provider.health_check() else "unhealthy"
    except Exception:
        return "unconfigured"

async def check_embedding_service() -> str:
    try:
        from app.services.embeddings.manager import EmbeddingManager
        manager = EmbeddingManager()
        if manager.service.model is not None:
            return "healthy"
        return "unhealthy"
    except Exception:
        return "unconfigured"

async def check_vector_database() -> str:
    try:
        from app.core.vectorstore_config import vs_config
        return f"healthy ({vs_config.provider})"
    except Exception:
        return "unconfigured"

from app.monitoring.health import HealthMonitor

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint for production monitoring.
    """
    return HealthMonitor.check_health().model_dump()

@router.get("/health/providers", tags=["Health"])
async def providers_health_check():
    """
    Health check endpoint for all configured LLM providers.
    """
    import time
    import asyncio
    import os
    from app.infrastructure.llm_providers.factory import LLMProviderFactory, LLMProviderType
    
    results = {}
    
    routing_str = getattr(settings, "PROVIDER_ROUTING_ORDER", "gemini,openrouter")
    provider_types = []
    for prov_str in routing_str.split(","):
        try:
            provider_types.append(LLMProviderType(prov_str.strip().lower()))
        except ValueError:
            pass
            
    primary_provider = getattr(settings, "PRIMARY_PROVIDER", "gemini")
    fallback_provider = getattr(settings, "FALLBACK_PROVIDER", "openrouter")
    
    async def check_single_provider(prov_type: LLMProviderType, priority: int):
        start_time = time.time()
        prov_name = prov_type.value
        configured = False
        reachable = False
        authenticated = False
        error_msg = ""
        model_name = "unknown"
        
        try:
            provider = LLMProviderFactory.get_provider(prov_type)
            prov_name = provider.provider_name
            # Check if API key exists
            configured = hasattr(provider, "api_key") and bool(provider.api_key)
            
            if configured:
                try:
                    # Execute with strict timeout
                    is_healthy = await asyncio.wait_for(provider.health_check(), timeout=5.0)
                    if is_healthy:
                        reachable = True
                        authenticated = True
                    else:
                        reachable = True
                        authenticated = False
                        error_msg = "Authentication failed or provider returned unhealthy status"
                except asyncio.TimeoutError:
                    reachable = False
                    error_msg = "Connection timeout exceeded"
                except Exception:
                    reachable = False
                    error_msg = "Connection or protocol error occurred"
            else:
                error_msg = "Provider API Key not configured"
                
            if prov_type.value == "gemini":
                model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            elif prov_type.value == "openrouter":
                model_name = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
            elif prov_type.value == "anthropic":
                model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            elif prov_type.value == "deepseek":
                model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            else:
                model_name = "default"
                
        except Exception:
            error_msg = "Provider failed to initialize"

        latency = int((time.time() - start_time) * 1000)
        
        is_primary = (prov_type.value == primary_provider)
        is_fallback = (prov_type.value == fallback_provider)
        status = "healthy" if (configured and reachable and authenticated) else "unhealthy"
        
        # Ensure fallback availability boolean makes sense
        fb_avail = True if (is_fallback and status == "healthy") else False
        
        return prov_type.value, {
            "name": prov_name,
            "status": status,
            "configuration_status": "configured" if configured else "unconfigured",
            "availability": "available" if (reachable and authenticated) else "unavailable",
            "authentication": "authenticated" if authenticated else "unauthenticated",
            "model_name": model_name,
            "latency_ms": latency,
            "error_reason": error_msg,
            "is_primary": is_primary,
            "is_secondary": is_fallback,
            "is_fallback_available": fb_avail,
            "priority_rank": priority + 1
        }
        
    tasks = []
    for i, prov_type in enumerate(provider_types):
        tasks.append(check_single_provider(prov_type, i))
        
    gathered = await asyncio.gather(*tasks)
    
    total_healthy = 0
    for key, data in gathered:
        results[key] = data
        if data["status"] == "healthy":
            total_healthy += 1
            
    return {
        "summary": {
            "total_configured_routes": len(provider_types),
            "healthy": total_healthy,
            "unhealthy": len(provider_types) - total_healthy,
            "default_provider": primary_provider
        },
        "providers": results
    }
