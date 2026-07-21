from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.orchestrator import OrchestratorRequest, NormalizedResponse
from app.orchestrator.orchestrator import AIOrchestrator
from app.core.exceptions import OrchestratorException, OrchestratorValidationError

router = APIRouter()

@router.post(
    "/execute",
    response_model=NormalizedResponse,
    summary="Execute AI Orchestrator Workflow",
    description="Central entry point for Spring Boot to communicate with the entire AI backend."
)
async def execute_orchestrator(request: OrchestratorRequest):
    try:
        return await AIOrchestrator.handle_request(request)
    except OrchestratorValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OrchestratorException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
