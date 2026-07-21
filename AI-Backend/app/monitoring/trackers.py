import time
import functools
from app.monitoring.metrics import metrics_collector, ExecutionLogger

class RequestTracker:
    @staticmethod
    def track_agent(agent_name: str):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start = time.time()
                success = True
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    latency = (time.time() - start) * 1000
                    metrics_collector.record_request(agent_name, latency, success)
                    ExecutionLogger.log_execution("AGENT", agent_name, success, latency)
            return wrapper
        return decorator

class ProviderUsageTracker:
    @staticmethod
    def track_provider(provider_name: str):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start = time.time()
                success = True
                fallback = kwargs.get("fallback", False)
                tokens = 0
                try:
                    result = await func(*args, **kwargs)
                    # Simple heuristic to grab tokens if it exists on result
                    if hasattr(result, "usage"):
                        tokens = getattr(result.usage, "total_tokens", 0)
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    latency = (time.time() - start) * 1000
                    metrics_collector.record_provider(provider_name, latency, success, tokens, fallback)
            return wrapper
        return decorator
