import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming requests, their methods, paths, 
    and processing times for basic APM (Application Performance Monitoring).
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        client_ip = request.client.host if request.client else "Unknown"
        user_agent = request.headers.get("user-agent", "Unknown")
        
        logger.info(
            f"API Request | {request.method} {request.url.path} "
            f"| Status: {response.status_code} "
            f"| Time: {process_time:.4f}s "
            f"| IP: {client_ip} "
            f"| UserAgent: {user_agent}"
        )
        return response
