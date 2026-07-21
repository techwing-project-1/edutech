from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logger import logger
from app.core.config import settings

# OpenSearch Phase 1 imports
from app.infrastructure.opensearch.client import opensearch_manager
from app.infrastructure.opensearch.logger import opensearch_logger
from app.infrastructure.opensearch.exceptions import OpenSearchException

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown events.
    Future DB and AI resource initialization belongs here.
    """
    # --- Startup ---
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode.")
    logger.info("Initializing AI Foundation and DB Connections...")
    
    # Phase 1: OpenSearch Infrastructure Initialization (Non-blocking)
    logger.info("Starting Phase 1 OpenSearch Validation...")
    try:
        # Check connection and health
        status = opensearch_manager.check_connection()
        opensearch_logger.info(f"OpenSearch initialization complete. Status: {status}")
    except OpenSearchException as e:
        opensearch_logger.warning(f"OpenSearch is unavailable or misconfigured: {str(e)}")
        opensearch_logger.warning("Application is starting in degraded mode. Vector retrieval features will fail.")
    except Exception as e:
        opensearch_logger.error(f"Unexpected error validating OpenSearch: {str(e)}")
        opensearch_logger.warning("Application is starting in degraded mode. Vector retrieval features will fail.")
    
    from app.services.llm.health_monitor import ProviderHealthMonitor
    ProviderHealthMonitor.start_background_checks()
    
    yield  # Yield control back to FastAPI
    
    # --- Shutdown ---
    logger.info(f"Shutting down {settings.PROJECT_NAME}.")
    logger.info("Cleaning up AI Foundation and DB Connections...")
