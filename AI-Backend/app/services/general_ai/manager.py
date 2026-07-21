from app.domain.schemas.general_ai import GeneralAIRequest, GeneralAIResponse
from app.services.general_ai.service import GeneralAIService

class GeneralAIManager:
    """
    High-level Orchestrator / Facade for the General AI Chat Engine.
    """
    
    @staticmethod
    async def chat(request: GeneralAIRequest) -> GeneralAIResponse:
        service = GeneralAIService()
        return await service.execute_chat(request)
