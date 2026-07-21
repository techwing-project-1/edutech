from typing import Dict, List, Optional
from app.domain.schemas.reminder_agent import ReminderResponse

class ReminderScheduler:
    """In-memory store for tracking and scheduling reminders."""
    def __init__(self):
        self._store: Dict[str, ReminderResponse] = {}
        
    def schedule(self, reminder: ReminderResponse) -> None:
        self._store[reminder.reminder_id] = reminder
        
    def get_by_user(self, user_id: str) -> List[ReminderResponse]:
        return [r for r in self._store.values() if r.user_id == user_id]
        
    def delete(self, reminder_id: str) -> bool:
        if reminder_id in self._store:
            del self._store[reminder_id]
            return True
        return False

# Global instance for mock persistence
reminder_scheduler = ReminderScheduler()
