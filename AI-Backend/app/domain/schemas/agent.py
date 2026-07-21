from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class AgentType(str, Enum):
    CALENDAR = "CALENDAR"
    ASSIGNMENT = "ASSIGNMENT"
    STUDY_PLANNER = "STUDY_PLANNER"
    REMINDER = "REMINDER"
    PROGRESS_TRACKING = "PROGRESS_TRACKING"
    NOTIFICATION = "NOTIFICATION"

class AgentRequest(BaseModel):
    """
    Standard request model for invoking an agent.
    """
    agent_type: AgentType = Field(..., description="The type of intelligent agent to invoke")
    user_id: str = Field(..., description="The ID of the student")
    query: str = Field(..., description="The user's query or the task to perform")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context parameters")

class AgentResponse(BaseModel):
    """
    Standard response model for agent execution.
    """
    agent_type: AgentType = Field(..., description="The agent that executed the task")
    result: str = Field(..., description="The outcome of the agent's action")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    actions_taken: List[str] = Field(default_factory=list, description="A list of actions the agent performed")
