from app.domain.schemas.notification import NotificationRequest, BulkNotificationRequest
from app.core.exceptions import NotificationValidationError
from datetime import datetime

class NotificationValidator:
    """Validates Notification requests."""
    
    @staticmethod
    def validate_request(request: NotificationRequest) -> None:
        if not request.user_id or not request.user_id.strip():
            raise NotificationValidationError("User ID cannot be empty")
        if not request.title or not request.title.strip():
            raise NotificationValidationError("Title cannot be empty")
        if not request.message or not request.message.strip():
            raise NotificationValidationError("Message cannot be empty")
        if not request.delivery_types:
            raise NotificationValidationError("At least one delivery type is required")
            
    @staticmethod
    def validate_bulk_request(request: BulkNotificationRequest) -> None:
        if not request.requests:
            raise NotificationValidationError("Bulk request must contain at least one notification")
        for req in request.requests:
            NotificationValidator.validate_request(req)
