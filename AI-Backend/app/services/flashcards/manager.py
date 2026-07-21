from app.domain.schemas.flashcards import FlashcardRequest, FlashcardResponse
from app.services.flashcards.service import FlashcardService

class FlashcardManager:
    """
    Facade for the Flashcard Generator Module.
    Exposes high-level methods to the API layer, wrapping the core FlashcardService.
    """
    
    def __init__(self):
        self.service = FlashcardService()

    async def generate(self, request: FlashcardRequest) -> FlashcardResponse:
        """
        Generates structured flashcards based on the provided request configuration.
        """
        return await self.service.generate_flashcards(request)
