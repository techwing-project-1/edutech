from app.domain.schemas.flashcards import FlashcardRequest, FlashcardType, FlashcardDifficulty
from app.core.exceptions import FlashcardValidationError

class FlashcardValidator:
    """
    Validates input requests for the Flashcards Generator.
    """
    
    @staticmethod
    def validate_request(request: FlashcardRequest) -> None:
        """
        Validates the incoming flashcard request.
        """
        if not request.topic or not request.topic.strip():
            raise FlashcardValidationError("Topic cannot be empty")
            
        if request.creativity < 0.0 or request.creativity > 1.0:
            raise FlashcardValidationError("Creativity must be between 0.0 and 1.0")
            
        if request.number_of_cards < 1 or request.number_of_cards > 50:
            raise FlashcardValidationError("Number of cards must be between 1 and 50")
            
        if request.flashcard_type not in [m.value for m in FlashcardType]:
            raise FlashcardValidationError(f"Invalid flashcard type: {request.flashcard_type}")
            
        if request.difficulty not in [m.value for m in FlashcardDifficulty]:
            raise FlashcardValidationError(f"Invalid difficulty level: {request.difficulty}")
