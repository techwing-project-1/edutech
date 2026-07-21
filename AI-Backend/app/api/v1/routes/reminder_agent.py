from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.domain.schemas.reminder_agent import ReminderRequest, ReminderListResponse
from app.agents.reminder.manager import ReminderManager
from app.core.exceptions import ReminderAgentException, ReminderAgentValidationError
import app.agents.reminder.agent # Register the agent

router = APIRouter()

def get_manager():
    return ReminderManager()

@router.post(
    "/create",
    response_model=ReminderListResponse,
    summary="Create Reminders",
    description="Generates reminders from the study plan and pushes them to the Notification Engine."
)
async def create_reminders(
    request: ReminderRequest,
    manager: ReminderManager = Depends(get_manager)
):
    try:
        return await manager.create(request)
    except ReminderAgentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ReminderAgentException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get(
    "/{user_id}",
    response_model=ReminderListResponse,
    summary="Get User Reminders",
)
def get_reminders(
    user_id: str,
    manager: ReminderManager = Depends(get_manager)
):
    return manager.get_by_user(user_id)

@router.delete(
    "/{id}",
    summary="Delete Reminder",
)
def delete_reminder(
    id: str,
    manager: ReminderManager = Depends(get_manager)
):
    success = manager.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"success": True}
