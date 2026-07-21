from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.study_planner import StudyPlannerRequest, StudyPlannerResponse
from app.agents.study_planner.manager import StudyPlannerManager
from app.core.exceptions import StudyPlannerException, StudyPlannerValidationError
import app.agents.study_planner.agent # Register the agent

router = APIRouter()

def get_manager():
    return StudyPlannerManager()

@router.post(
    "/generate",
    response_model=StudyPlannerResponse,
    summary="Generate Study Plan",
    description="Generates personalized study schedules, daily targets, and exam prep strategies."
)
async def generate_plan(
    request: StudyPlannerRequest,
    manager: StudyPlannerManager = Depends(get_manager)
):
    try:
        response = await manager.generate(request)
        return response
    except StudyPlannerValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StudyPlannerException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
