from app.domain.schemas.reminder_agent import ReminderRequest
from app.core.exceptions import ReminderAgentValidationError

class ReminderAgentValidator:
    """Validates input requests for the Reminder Agent."""
    
    @staticmethod
    def validate_request(request: ReminderRequest) -> None:
        if not request.user_id or not request.user_id.strip():
            raise ReminderAgentValidationError("User ID cannot be empty")
