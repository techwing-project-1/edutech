from typing import Any
from app.agents.interfaces import BaseAgent
from app.domain.schemas.agent import AgentRequest, AgentResponse, AgentType
from app.agents.calendar.service import CalendarService
from app.domain.schemas.calendar_agent import CalendarAgentRequest
from app.agents.registry import AgentRegistry

class CalendarAgent(BaseAgent):
    """
    Intelligent agent for generating calendar events from assignment data.
    """
    
    def __init__(self):
        self.service = CalendarService()
        
    async def execute(self, request: AgentRequest) -> AgentResponse:
        # Convert generic agent request to specific calendar request
        calendar_req = CalendarAgentRequest(
            user_id=request.user_id,
            department=request.context.get("department"),
            semester=request.context.get("semester"),
            subject=request.context.get("subject"),
            section=request.context.get("section")
        )
        
        cal_res = await self.service.generate_calendar(
            calendar_req,
            query_override=request.query
        )
        
        result_json = cal_res.model_dump_json()
        
        return AgentResponse(
            agent_type=AgentType.CALENDAR,
            result=result_json,
            actions_taken=["assignment_extraction", "calendar_generation", "ics_export"],
            metadata=cal_res.metadata
        )

    async def get_memory(self, user_id: str) -> Any:
        return {}
        
    async def run_background_task(self, task_data: Any) -> None:
        pass

# Register the agent
AgentRegistry.register(AgentType.CALENDAR, CalendarAgent)
