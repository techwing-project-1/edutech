from app.domain.schemas.general_ai import GeneralAIRequest
from app.core.exceptions import GeneralAIException

class GeneralAIValidator:
    """
    Validates incoming chat requests for the General AI Assistant.
    """
    
    @staticmethod
    def validate_request(request: GeneralAIRequest) -> None:
        errors = {}
        
        if not request.query or not request.query.strip():
            errors["query"] = "Query cannot be empty."
            
        if request.session_id is not None and not isinstance(request.session_id, str):
            errors["session_id"] = "Session ID must be a string."
            
        if request.temperature < 0.0 or request.temperature > 2.0:
            errors["temperature"] = "Temperature must be between 0.0 and 2.0."
            
        if request.max_tokens < 1 or request.max_tokens > 8192:
            errors["max_tokens"] = "max_tokens must be between 1 and 8192."
            
        if request.history is not None:
            if not isinstance(request.history, list):
                errors["history"] = "History must be a list."
            else:
                valid_roles = {"user", "assistant", "system", "tool"}
                for idx, msg in enumerate(request.history):
                    if not msg.role or msg.role.lower() not in valid_roles:
                        errors[f"history[{idx}].role"] = f"Invalid role. Must be one of {valid_roles}."
                    if not msg.content:
                        errors[f"history[{idx}].content"] = "Message content cannot be empty."
                        
        if errors:
            raise GeneralAIException(
                message="Validation Error: The request payload is invalid.",
                status_code=400,
                error_code="VALIDATION_ERROR",
                details={"errors": errors}
            )
