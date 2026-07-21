from typing import Any
from app.agents.interfaces import BaseAgent
from app.domain.schemas.agent import AgentRequest, AgentResponse, AgentType
from app.agents.assignment.service import AssignmentExtractionService
from app.domain.schemas.assignment_agent import AssignmentAgentRequest
from app.agents.registry import AgentRegistry

class AssignmentAgent(BaseAgent):
    """
    Intelligent agent for extracting assignments and deadlines.
    """
    
    def __init__(self):
        self.service = AssignmentExtractionService()
        
    async def execute(self, request: AgentRequest) -> AgentResponse:
        # Convert generic agent request to specific assignment request
        assignment_req = AssignmentAgentRequest(
            user_id=request.user_id,
            department=request.context.get("department"),
            semester=request.context.get("semester"),
            subject=request.context.get("subject"),
            section=request.context.get("section")
        )
        
        extraction_res = await self.service.extract_assignments(
            assignment_req,
            query_override=request.query
        )
        
        # Serialize the response to match AgentResponse result format
        result_json = extraction_res.model_dump_json()
        
        return AgentResponse(
            agent_type=AgentType.ASSIGNMENT,
            result=result_json,
            actions_taken=["rag_extraction"],
            metadata=extraction_res.metadata
        )

    async def get_memory(self, user_id: str) -> Any:
        return {}
        
    async def run_background_task(self, task_data: Any) -> None:
        pass

# Register the agent
AgentRegistry.register(AgentType.ASSIGNMENT, AssignmentAgent)
