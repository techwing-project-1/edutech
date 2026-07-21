import logging
import sys
import json
from contextvars import ContextVar
from datetime import datetime, timezone
from app.core.config import settings

# Context variable to hold request ID across async tasks
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")

class StructuredJsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx_var.get(),
            "environment": settings.ENVIRONMENT
        }
        
        # Add extra fields if passed via 'extra' dictionary
        if hasattr(record, "extra_info"):
            log_record.update(record.extra_info)
            
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging():
    """
    Configures the central logger for the application.
    Outputs structured JSON logs suitable for production environments.
    """
    handler = logging.StreamHandler(sys.stdout)
    
    # In development, you might want simple logs, but for prod, use JSON
    if settings.ENVIRONMENT.lower() == "production":
        handler.setFormatter(StructuredJsonFormatter())
    else:
        log_format = "%(asctime)s - %(levelname)s - [%(request_id)s] - %(message)s"
        # We need a custom filter to inject request_id into standard formatter
        class RequestIdFilter(logging.Filter):
            def filter(self, record):
                record.request_id = request_id_ctx_var.get()
                return True
        handler.addFilter(RequestIdFilter())
        handler.setFormatter(logging.Formatter(log_format))

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        handlers=[handler]
    )

    # Prevent duplicate logs if basicConfig was already called
    logger = logging.getLogger("curriculamind")
    logger.setLevel(settings.LOG_LEVEL)
    logger.propagate = False
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

# Export central logger
logger = setup_logging()
