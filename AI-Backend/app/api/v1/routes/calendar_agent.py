from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.calendar_agent import CalendarAgentRequest, CalendarAgentResponse
from app.agents.calendar.manager import CalendarManager
from app.core.exceptions import CalendarAgentException, CalendarAgentValidationError
import app.agents.calendar.agent # Register the agent

router = APIRouter()

def get_manager():
    return CalendarManager()

@router.post(
    "/generate",
    response_model=CalendarAgentResponse,
    summary="Generate Calendar Schedule",
    description="Generates study schedules and calendar events using the Calendar Intelligence Agent."
)
async def generate_calendar(
    request: CalendarAgentRequest,
    manager: CalendarManager = Depends(get_manager)
):
    try:
        response = await manager.generate(request)
        return response
    except CalendarAgentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CalendarAgentException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
