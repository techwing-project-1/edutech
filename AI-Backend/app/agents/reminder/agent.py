from typing import Any
from app.agents.interfaces import BaseAgent
from app.domain.schemas.agent import AgentRequest, AgentResponse, AgentType
from app.agents.reminder.service import ReminderService
from app.domain.schemas.reminder_agent import ReminderRequest, ReminderScheduleTime
from app.agents.registry import AgentRegistry

class ReminderAgent(BaseAgent):
    """
    Intelligent agent for generating and scheduling reminders from study plans.
    """
    
    def __init__(self):
        self.service = ReminderService()
        
    async def execute(self, request: AgentRequest) -> AgentResponse:
        
        time_str = request.context.get("schedule_time", "ONE_DAY").upper()
        if time_str not in [e.value for e in ReminderScheduleTime]:
            time_str = "ONE_DAY"
            
        rem_req = ReminderRequest(
            user_id=request.user_id,
            department=request.context.get("department"),
            semester=request.context.get("semester"),
            subject=request.context.get("subject"),
            section=request.context.get("section"),
            schedule_time=ReminderScheduleTime(time_str)
        )
        
        rems = await self.service.create_reminders(rem_req)
        result_json = rems.model_dump_json()
        
        return AgentResponse(
            agent_type=AgentType.REMINDER,
            result=result_json,
            actions_taken=["study_plan_retrieval", "reminder_generation", "notification_dispatch"],
            metadata={}
        )

    async def get_memory(self, user_id: str) -> Any:
        return {}
        
    async def run_background_task(self, task_data: Any) -> None:
        pass

# Register the agent
AgentRegistry.register(AgentType.REMINDER, ReminderAgent)
