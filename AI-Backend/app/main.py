from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.routes import health
from app.core.exceptions import add_exception_handlers
from app.core.startup import lifespan
from app.api.middleware.logging import RequestLoggingMiddleware

def create_app() -> FastAPI:
    """
    Application factory for the FastAPI AI Backend.
    Sets up routers, middleware, exception handlers, and lifespans.
    """
    from app.monitoring.metrics import MetricsMiddleware
    from app.infrastructure.database.session import init_db

    async def custom_lifespan(app: FastAPI):
        # Setup DB
        await init_db()
        # Call original lifespan if needed, or inline it here
        async with lifespan(app):
            yield

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Production-grade AI Backend featuring robust conversation memory, streaming, and multi-provider LLM routing.",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=custom_lifespan
    )

    # Custom OpenAPI Schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema
        
    app.openapi = custom_openapi

    # Add Middleware
    origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With", "X-Request-ID"],
        )
        
    from app.api.middleware.rate_limiter import SimpleRateLimitMiddleware
    app.add_middleware(SimpleRateLimitMiddleware, rate_limit=100, window_seconds=60)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(MetricsMiddleware)

    # Add Exception Handlers
    add_exception_handlers(app)

    # Include Routers
    # Health check at root for easy load balancer access
    app.include_router(health.router)
    
    # Future v1 API routes (e.g., /api/v1/rag, /api/v1/llm)
    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()
