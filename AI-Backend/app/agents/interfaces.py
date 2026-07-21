from abc import ABC, abstractmethod
from typing import Any
from app.domain.schemas.agent import AgentRequest, AgentResponse

class BaseAgent(ABC):
    """
    Base interface for all OpenClaw educational agents.
    Enforces the agent pattern and solid principles.
    """
    
    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Executes the main task of the agent.
        """
        pass
        
    @abstractmethod
    async def get_memory(self, user_id: str) -> Any:
        """
        Prepare agent memory interface.
        """
        pass
        
    @abstractmethod
    async def run_background_task(self, task_data: Any) -> None:
        """
        Prepare future background task support.
        """
        pass
