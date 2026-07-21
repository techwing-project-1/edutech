from app.domain.schemas.study_planner import StudyPlannerRequest
from app.core.exceptions import StudyPlannerValidationError

class StudyPlannerValidator:
    """Validates input requests for the Study Planner Agent."""
    
    @staticmethod
    def validate_request(request: StudyPlannerRequest) -> None:
        if not request.user_id or not request.user_id.strip():
            raise StudyPlannerValidationError("User ID cannot be empty")
        if request.study_hours_per_day <= 0:
            raise StudyPlannerValidationError("Study hours must be greater than 0")
