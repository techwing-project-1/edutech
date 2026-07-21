from app.domain.schemas.study_notes import StudyNotesRequest, StudyNotesResponse
from app.services.study_notes.service import StudyNotesService

class StudyNotesManager:
    """
    Facade for the Study Notes Generator Module.
    Exposes high-level methods to the API layer, wrapping the core StudyNotesService.
    """
    
    def __init__(self):
        self.service = StudyNotesService()

    async def generate(self, request: StudyNotesRequest) -> StudyNotesResponse:
        """
        Generates study notes based on the provided request configuration.
        """
        return await self.service.generate_notes(request)
