from app.domain.schemas.content_generation import ContentGenerationRequest, ContentGenerationResponse
from app.services.content_generation.service import ContentGenerationService

class ContentGenerationManager:
    """
    Facade for the Content Generation Engine.
    Exposes high-level methods to the API layer, wrapping the core service.
    """
    
    def __init__(self):
        self.service = ContentGenerationService()

    async def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """
        Generates content based on the provided request configuration.
        """
        return await self.service.generate(request)
