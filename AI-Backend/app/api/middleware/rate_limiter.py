from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from typing import Dict, Tuple

class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """
    A simple in-memory rate limiter to protect against DoS and LLM quota exhaustion.
    Production systems should use Redis or similar distributed stores.
    """
    def __init__(self, app, rate_limit: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        # dict mapping client IP to (count, window_start_time)
        self.clients: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get client IP (fallback to 127.0.0.1)
        client_ip = request.client.host if request.client else "127.0.0.1"
        
        current_time = time.time()
        
        if client_ip in self.clients:
            count, start_time = self.clients[client_ip]
            if current_time - start_time > self.window_seconds:
                # Reset window
                self.clients[client_ip] = (1, current_time)
            else:
                if count >= self.rate_limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Rate limit exceeded. Please try again later."}
                    )
                self.clients[client_ip] = (count + 1, start_time)
        else:
            self.clients[client_ip] = (1, current_time)
            
        return await call_next(request)
