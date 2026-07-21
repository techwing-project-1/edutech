from typing import Dict, List, Optional
from app.domain.schemas.notification import NotificationResponse, NotificationStatus
from datetime import datetime, timezone

class NotificationHistory:
    """In-memory store for notification history. Will be replaced by DB."""
    def __init__(self):
        self._store: Dict[str, NotificationResponse] = {}
        
    def save(self, notification: NotificationResponse) -> None:
        self._store[notification.notification_id] = notification
        
    def get(self, notification_id: str) -> Optional[NotificationResponse]:
        return self._store.get(notification_id)
        
    def get_by_user(self, user_id: str) -> List[NotificationResponse]:
        return [n for n in self._store.values() if n.user_id == user_id]
        
    def update_status(self, notification_id: str, status: NotificationStatus) -> bool:
        if notification_id in self._store:
            # We must create a new object or mutate carefully. Since Pydantic models are mutable:
            self._store[notification_id].status = status
            return True
        return False

# Global instance
notification_history = NotificationHistory()
