from app.domain.schemas.calendar_agent import CalendarAgentRequest, CalendarAgentResponse
from app.agents.calendar.service import CalendarService
from app.agents.calendar.validator import CalendarAgentValidator

class CalendarManager:
    """Manager for handling direct Calendar generation requests."""
    def __init__(self):
        self.service = CalendarService()
        
    async def generate(self, request: CalendarAgentRequest) -> CalendarAgentResponse:
        CalendarAgentValidator.validate_request(request)
        return await self.service.generate_calendar(request)
