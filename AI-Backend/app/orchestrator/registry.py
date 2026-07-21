from typing import Callable, Dict
from app.domain.schemas.orchestrator import AIMode

class ServiceRegistry:
    """Registry mapping AIMode to internal execution handlers."""
    
    _handlers: Dict[AIMode, Callable] = {}
    
    @classmethod
    def register(cls, mode: AIMode, handler: Callable):
        cls._handlers[mode] = handler
        
    @classmethod
    def get_handler(cls, mode: AIMode) -> Callable:
        return cls._handlers.get(mode)
