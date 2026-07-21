import time
import threading
import uuid
from typing import Dict, Any, List
from collections import deque
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger, request_id_ctx_var

class RealtimeMetricsCollector:
    """Thread-safe, in-memory storage for all application runtime metrics."""
    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = time.time()
        
        self.total_requests = 0
        self.total_errors = 0
        self.total_latency_ms = 0.0
        self.concurrent_requests = 0
        
        # Keep rolling window of last 10,000 latencies for accurate percentiles
        self.latency_window = deque(maxlen=10000)
        
        # Token metrics
        self.total_tokens = 0
        
        # External dependencies latencies
        self.gemini_latency_window = deque(maxlen=10000)
        self.opensearch_latency_window = deque(maxlen=10000)
        self.agent_execution_latency_window = deque(maxlen=10000)
        
        # Sub-systems
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.providers: Dict[str, Dict[str, Any]] = {}

    def _calculate_percentiles(self, window: deque) -> Dict[str, float]:
        if not window:
            return {"min": 0.0, "max": 0.0, "median": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_latencies = sorted(list(window))
        n = len(sorted_latencies)
        return {
            "min": sorted_latencies[0],
            "max": sorted_latencies[-1],
            "median": sorted_latencies[int(n * 0.50)],
            "p90": sorted_latencies[int(n * 0.90)],
            "p95": sorted_latencies[int(n * 0.95)],
            "p99": sorted_latencies[int(n * 0.99)],
        }

    def get_overall_latencies(self) -> Dict[str, float]:
        with self.lock:
            return self._calculate_percentiles(self.latency_window)

    def get_avg_metric(self, window: deque) -> float:
        with self.lock:
            if not window:
                return 0.0
            return sum(window) / len(window)

    def increment_concurrent(self):
        with self.lock:
            self.concurrent_requests += 1

    def decrement_concurrent(self):
        with self.lock:
            self.concurrent_requests = max(0, self.concurrent_requests - 1)

    def record_api_request(self, latency_ms: float, success: bool):
        with self.lock:
            self.total_requests += 1
            self.total_latency_ms += latency_ms
            self.latency_window.append(latency_ms)
            if not success:
                self.total_errors += 1

    def record_agent_execution(self, agent_name: str, latency_ms: float, success: bool):
        with self.lock:
            self.agent_execution_latency_window.append(latency_ms)
            if agent_name not in self.agents:
                self.agents[agent_name] = {"calls": 0, "errors": 0, "latency": 0.0}
            
            self.agents[agent_name]["calls"] += 1
            self.agents[agent_name]["latency"] += latency_ms
            if not success:
                self.agents[agent_name]["errors"] += 1

    def record_provider_execution(self, provider: str, latency_ms: float, success: bool, tokens: int = 0, is_fallback: bool = False, is_quota_error: bool = False):
        with self.lock:
            self.total_tokens += tokens
            if provider.lower() == "gemini":
                self.gemini_latency_window.append(latency_ms)
                
            if provider not in self.providers:
                self.providers[provider] = {"requests": 0, "tokens": 0, "latency": 0.0, "fallbacks": 0, "errors": 0, "quota_errors": 0}
                
            self.providers[provider]["requests"] += 1
            self.providers[provider]["latency"] += latency_ms
            self.providers[provider]["tokens"] += tokens
            if not success:
                self.providers[provider]["errors"] += 1
            if is_quota_error:
                self.providers[provider]["quota_errors"] += 1
            if is_fallback:
                self.providers[provider]["fallbacks"] += 1

    def record_opensearch_query(self, latency_ms: float):
        with self.lock:
            self.opensearch_latency_window.append(latency_ms)

metrics_collector = RealtimeMetricsCollector()

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject request IDs and track top-level request metrics accurately.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        token = request_id_ctx_var.set(request_id)
        start_time = time.time()
        
        metrics_collector.increment_concurrent()
        success = True
        try:
            response = await call_next(request)
            
            if response.status_code >= 500:
                success = False
                
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            success = False
            logger.error(f"Request failed: {str(e)}", extra={"extra_info": {"path": request.url.path}})
            raise
        finally:
            latency_ms = (time.time() - start_time) * 1000.0
            metrics_collector.record_api_request(latency_ms=latency_ms, success=success)
            metrics_collector.decrement_concurrent()
            request_id_ctx_var.reset(token)

class ExecutionLogger:
    @staticmethod
    def log_execution(execution_id: str, mode: str, success: bool, latency: float):
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"[EXECUTION] ID: {execution_id} | Mode: {mode} | Status: {status} | Latency: {latency:.2f}ms")

def record_llm_metrics(provider: str, model: str, latency_ms: float, tokens: int, is_fallback: bool = False, success: bool = True, is_quota_error: bool = False):
    metrics_collector.record_provider_execution(provider, latency_ms, success, tokens, is_fallback, is_quota_error)
    logger.info(f"LLM Metrics - Provider: {provider}, Model: {model}, Latency: {latency_ms:.2f}ms, Tokens: {tokens}, Fallback: {is_fallback}")

def record_agent_metrics(agent_name: str, latency_ms: float, success: bool):
    metrics_collector.record_agent_execution(agent_name, latency_ms, success)
    
def record_opensearch_metrics(latency_ms: float):
    metrics_collector.record_opensearch_query(latency_ms)
