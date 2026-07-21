from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.domain.schemas.notification import (
    NotificationRequest, NotificationResponse, NotificationListResponse, NotificationUpdateResponse
)
from app.services.notification.manager import NotificationManager
from app.core.exceptions import NotificationException, NotificationValidationError

router = APIRouter()

def get_manager():
    return NotificationManager()

@router.post(
    "/create",
    response_model=NotificationResponse,
    summary="Create Notification",
    description="Dispatches a notification via the Notification Engine."
)
async def create_notification(
    request: NotificationRequest,
    manager: NotificationManager = Depends(get_manager)
):
    try:
        return await manager.create(request)
    except NotificationValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotificationException as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Get User Notifications",
)
def get_notifications(
    user_id: str,
    manager: NotificationManager = Depends(get_manager)
):
    notifs = manager.get_by_user(user_id)
    return NotificationListResponse(total=len(notifs), notifications=notifs)

@router.put(
    "/{id}/read",
    response_model=NotificationUpdateResponse,
    summary="Mark Notification as Read",
)
def mark_read(
    id: str,
    manager: NotificationManager = Depends(get_manager)
):
    return manager.mark_as_read(id)
