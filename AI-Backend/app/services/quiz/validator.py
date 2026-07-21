from app.domain.schemas.quiz import QuizRequest, QuizType, QuizDifficulty
from app.core.exceptions import QuizValidationError

class QuizValidator:
    """
    Validates input requests for the Quiz Generator.
    """
    
    @staticmethod
    def validate_request(request: QuizRequest) -> None:
        """
        Validates the incoming quiz request.
        """
        if not request.topic or not request.topic.strip():
            raise QuizValidationError("Topic cannot be empty")
            
        if request.creativity < 0.0 or request.creativity > 1.0:
            raise QuizValidationError("Creativity must be between 0.0 and 1.0")
            
        if request.number_of_questions < 1 or request.number_of_questions > 50:
            raise QuizValidationError("Number of questions must be between 1 and 50")
            
        if request.quiz_type not in [m.value for m in QuizType]:
            raise QuizValidationError(f"Invalid quiz type: {request.quiz_type}")
            
        if request.difficulty not in [m.value for m in QuizDifficulty]:
            raise QuizValidationError(f"Invalid difficulty level: {request.difficulty}")
