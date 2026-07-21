from app.domain.schemas.summary import SummaryRequest, SummaryType
from app.core.exceptions import SummaryValidationError

class SummaryValidator:
    """
    Validates input requests for the Summary Generator.
    """
    
    @staticmethod
    def validate_request(request: SummaryRequest) -> None:
        """
        Validates the incoming summary request.
        """
        if not request.topic or not request.topic.strip():
            raise SummaryValidationError("Topic cannot be empty")
            
        if request.creativity < 0.0 or request.creativity > 1.0:
            raise SummaryValidationError("Creativity must be between 0.0 and 1.0")
            
        if request.length_words < 50 or request.length_words > 2000:
            raise SummaryValidationError("Summary length must be between 50 and 2000 words")
            
        if request.summary_type not in [m.value for m in SummaryType]:
            raise SummaryValidationError(f"Invalid summary type: {request.summary_type}")
