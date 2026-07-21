from app.domain.schemas.orchestrator import OrchestratorRequest, NormalizedResponse
from app.orchestrator.workflow import WorkflowManager
from app.core.exceptions import OrchestratorValidationError

class AIOrchestrator:
    """Facade for the complete AI Orchestrator Layer."""
    
    @staticmethod
    async def handle_request(request: OrchestratorRequest) -> NormalizedResponse:
        if not request.user_id:
            raise OrchestratorValidationError("User ID is required for AI Orchestrator")
            
        return await WorkflowManager.execute(request)
