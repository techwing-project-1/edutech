from app.domain.schemas.reminder_agent import ReminderRequest, ReminderListResponse
from app.agents.reminder.service import ReminderService
from app.agents.reminder.validator import ReminderAgentValidator

class ReminderManager:
    """Manager for handling Reminder generation requests."""
    def __init__(self):
        self.service = ReminderService()
        
    async def create(self, request: ReminderRequest) -> ReminderListResponse:
        ReminderAgentValidator.validate_request(request)
        return await self.service.create_reminders(request)
        
    def get_by_user(self, user_id: str) -> ReminderListResponse:
        return self.service.get_by_user(user_id)
        
    def delete(self, reminder_id: str) -> bool:
        return self.service.delete_reminder(reminder_id)
