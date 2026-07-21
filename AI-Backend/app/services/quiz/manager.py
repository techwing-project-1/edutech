from app.domain.schemas.quiz import QuizRequest, QuizResponse
from app.services.quiz.service import QuizService

class QuizManager:
    """
    Facade for the Quiz Generator Module.
    Exposes high-level methods to the API layer, wrapping the core QuizService.
    """
    
    def __init__(self):
        self.service = QuizService()

    async def generate(self, request: QuizRequest) -> QuizResponse:
        """
        Generates a structured quiz based on the provided request configuration.
        """
        return await self.service.generate_quiz(request)
