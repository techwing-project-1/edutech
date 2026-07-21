from app.domain.schemas.assignment_agent import AssignmentAgentRequest, AssignmentAgentResponse
from app.agents.assignment.service import AssignmentExtractionService
from app.agents.assignment.validator import AssignmentAgentValidator

class AssignmentManager:
    """Manager for handling direct Assignment Extraction requests outside the generic Agent Orchestrator."""
    def __init__(self):
        self.service = AssignmentExtractionService()
        
    async def extract(self, request: AssignmentAgentRequest) -> AssignmentAgentResponse:
        AssignmentAgentValidator.validate_request(request)
        return await self.service.extract_assignments(request)
