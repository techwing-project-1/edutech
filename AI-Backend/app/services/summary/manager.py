from app.domain.schemas.summary import SummaryRequest, SummaryResponse
from app.services.summary.service import SummaryService

class SummaryManager:
    """
    Facade for the Summary Generator Module.
    Exposes high-level methods to the API layer, wrapping the core SummaryService.
    """
    
    def __init__(self):
        self.service = SummaryService()

    async def generate(self, request: SummaryRequest) -> SummaryResponse:
        """
        Generates a summary based on the provided request configuration.
        """
        return await self.service.generate_summary(request)
