from typing import Dict, Type
from app.domain.schemas.agent import AgentType
from app.agents.interfaces import BaseAgent
from app.core.exceptions import AgentException

class AgentRegistry:
    """
    Registry for educational agents.
    Allows mapping AgentType to specific BaseAgent implementations.
    """
    
    _registry: Dict[AgentType, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, agent_type: AgentType, agent_class: Type[BaseAgent]) -> None:
        """Registers an agent class."""
        cls._registry[agent_type] = agent_class

    @classmethod
    def get_agent_class(cls, agent_type: AgentType) -> Type[BaseAgent]:
        """Retrieves an agent class."""
        if agent_type not in cls._registry:
            raise AgentException(f"No agent registered for type: {agent_type}")
        return cls._registry[agent_type]
