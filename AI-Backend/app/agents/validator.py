from app.domain.schemas.agent import AgentRequest, AgentType
from app.core.exceptions import AgentValidationError

class AgentValidator:
    """
    Validates agent requests.
    """
    
    @staticmethod
    def validate_request(request: AgentRequest) -> None:
        """
        Validates the incoming agent request.
        """
        if not request.query or not request.query.strip():
            raise AgentValidationError("Query cannot be empty")
            
        if not request.user_id or not request.user_id.strip():
            raise AgentValidationError("User ID cannot be empty")
            
        if request.agent_type not in [m.value for m in AgentType]:
            raise AgentValidationError(f"Invalid agent type: {request.agent_type}")
