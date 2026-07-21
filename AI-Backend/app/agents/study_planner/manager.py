from app.domain.schemas.study_planner import StudyPlannerRequest, StudyPlannerResponse
from app.agents.study_planner.service import StudyPlannerService
from app.agents.study_planner.validator import StudyPlannerValidator

class StudyPlannerManager:
    """Manager for handling Study Planner requests."""
    def __init__(self):
        self.service = StudyPlannerService()
        
    async def generate(self, request: StudyPlannerRequest) -> StudyPlannerResponse:
        StudyPlannerValidator.validate_request(request)
        return await self.service.generate_plan(request)
