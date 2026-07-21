from typing import List, Optional
from app.domain.schemas.notification import (
    NotificationRequest, NotificationResponse, BulkNotificationRequest, 
    NotificationUpdateResponse, NotificationStatus
)
from app.services.notification.engine import NotificationEngine
from app.services.notification.validator import NotificationValidator
from app.services.notification.history import notification_history

class NotificationManager:
    def __init__(self):
        self.engine = NotificationEngine()
        
    async def create(self, request: NotificationRequest) -> NotificationResponse:
        NotificationValidator.validate_request(request)
        return await self.engine.process_notification(request)
        
    async def create_bulk(self, request: BulkNotificationRequest) -> List[NotificationResponse]:
        NotificationValidator.validate_bulk_request(request)
        return await self.engine.process_bulk(request)
        
    def get_by_user(self, user_id: str) -> List[NotificationResponse]:
        return notification_history.get_by_user(user_id)
        
    def mark_as_read(self, notification_id: str) -> NotificationUpdateResponse:
        success = notification_history.update_status(notification_id, NotificationStatus.READ)
        return NotificationUpdateResponse(
            success=success,
            notification_id=notification_id,
            status=NotificationStatus.READ if success else NotificationStatus.FAILED
        )
