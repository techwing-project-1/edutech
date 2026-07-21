from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.assignment_agent import AssignmentAgentRequest, AssignmentAgentResponse
from app.agents.assignment.manager import AssignmentManager
from app.core.exceptions import AssignmentAgentException, AssignmentAgentValidationError
import app.agents.assignment.agent # Register the agent

router = APIRouter()

def get_manager():
    return AssignmentManager()

@router.post(
    "/extract",
    response_model=AssignmentAgentResponse,
    summary="Extract Assignments",
    description="Extracts assignments, projects, and deadlines using the Assignment Intelligence Agent."
)
async def extract_assignments(
    request: AssignmentAgentRequest,
    manager: AssignmentManager = Depends(get_manager)
):
    try:
        response = await manager.extract(request)
        return response
    except AssignmentAgentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AssignmentAgentException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
