import uuid
from datetime import datetime, timezone
from app.domain.schemas.notification import (
    NotificationRequest, NotificationResponse, NotificationStatus, BulkNotificationRequest
)
from app.services.notification.factory import NotificationFactory
from app.services.notification.formatter import NotificationFormatter
from app.services.notification.history import notification_history
from app.services.notification.queue import notification_queue
from app.core.logger import logger
from typing import List

class NotificationEngine:
    """Core logic for routing, formatting, and executing notifications."""
    
    async def process_notification(self, request: NotificationRequest) -> NotificationResponse:
        notif_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        response = NotificationResponse(
            notification_id=notif_id,
            user_id=request.user_id,
            title=request.title,
            message=request.message,
            category=request.category,
            priority=request.priority,
            status=NotificationStatus.PENDING,
            delivery_types=request.delivery_types,
            created_at=now,
            scheduled_for=request.scheduled_for,
            expires_at=request.expires_at,
            metadata=request.metadata or {}
        )
        
        # Save to history
        notification_history.save(response)
        
        # Enqueue for delivery
        await notification_queue.enqueue(self._execute_delivery, response)
        return response
        
    async def _execute_delivery(self, notification: NotificationResponse):
        """Internal worker method to actually deliver."""
        formatted_message = NotificationFormatter.format(
            NotificationRequest(
                user_id=notification.user_id,
                title=notification.title,
                message=notification.message,
                category=notification.category,
                priority=notification.priority,
                delivery_types=notification.delivery_types
            )
        )
        
        success_count = 0
        for dtype in notification.delivery_types:
            strategy = NotificationFactory.get_strategy(dtype)
            try:
                # Basic retry simulation could happen here
                success = await strategy.deliver(formatted_message, notification.user_id)
                if success:
                    success_count += 1
            except Exception as e:
                logger.error(f"Delivery failed for {dtype}: {e}")
                
        if success_count > 0:
            notification_history.update_status(notification.notification_id, NotificationStatus.SENT)
        else:
            notification.retry_count += 1
            notification_history.update_status(notification.notification_id, NotificationStatus.FAILED)
            
    async def process_bulk(self, request: BulkNotificationRequest) -> List[NotificationResponse]:
        responses = []
        for req in request.requests:
            res = await self.process_notification(req)
            responses.append(res)
        return responses
