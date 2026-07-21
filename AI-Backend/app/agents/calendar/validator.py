from app.domain.schemas.calendar_agent import CalendarAgentRequest
from app.core.exceptions import CalendarAgentValidationError

class CalendarAgentValidator:
    """Validates input requests for the Calendar Agent."""
    
    @staticmethod
    def validate_request(request: CalendarAgentRequest) -> None:
        if not request.user_id or not request.user_id.strip():
            raise CalendarAgentValidationError("User ID cannot be empty")
