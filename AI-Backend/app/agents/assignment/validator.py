from app.domain.schemas.assignment_agent import AssignmentAgentRequest
from app.core.exceptions import AssignmentAgentValidationError

class AssignmentAgentValidator:
    """Validates input requests for the Assignment Agent."""
    
    @staticmethod
    def validate_request(request: AssignmentAgentRequest) -> None:
        if not request.user_id or not request.user_id.strip():
            raise AssignmentAgentValidationError("User ID cannot be empty")
