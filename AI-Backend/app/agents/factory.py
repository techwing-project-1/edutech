from app.domain.schemas.agent import AgentType
from app.agents.interfaces import BaseAgent
from app.agents.registry import AgentRegistry

class AgentFactory:
    """
    Factory for instantiating the correct Agent based on AgentType.
    """
    
    @staticmethod
    def create_agent(agent_type: AgentType) -> BaseAgent:
        """
        Creates and returns an instance of the appropriate agent.
        Supports dependency injection in the future by passing kwargs here.
        """
        agent_class = AgentRegistry.get_agent_class(agent_type)
        return agent_class()
