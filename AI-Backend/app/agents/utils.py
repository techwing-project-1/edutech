import time
from typing import Callable, Any

def time_agent_execution(func: Callable) -> Callable:
    """
    Utility decorator to measure agent execution time.
    """
    async def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        if hasattr(result, 'metadata'):
            result.metadata['execution_time_seconds'] = duration
        return result
    return wrapper
