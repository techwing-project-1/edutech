from typing import Any
from app.agents.interfaces import BaseAgent
from app.domain.schemas.agent import AgentRequest, AgentResponse, AgentType
from app.agents.study_planner.service import StudyPlannerService
from app.domain.schemas.study_planner import StudyPlannerRequest, StudyIntensity
from app.agents.registry import AgentRegistry

class StudyPlannerAgent(BaseAgent):
    """
    Intelligent agent for generating study plans.
    """
    
    def __init__(self):
        self.service = StudyPlannerService()
        
    async def execute(self, request: AgentRequest) -> AgentResponse:
        # Extract additional context for specific parameters if provided
        study_hours = request.context.get("study_hours_per_day", 2.0)
        intensity_str = request.context.get("study_intensity", "NORMAL").upper()
        intensity = StudyIntensity(intensity_str) if intensity_str in [i.value for i in StudyIntensity] else StudyIntensity.NORMAL
        
        study_req = StudyPlannerRequest(
            user_id=request.user_id,
            department=request.context.get("department"),
            semester=request.context.get("semester"),
            subject=request.context.get("subject"),
            section=request.context.get("section"),
            study_hours_per_day=study_hours,
            study_intensity=intensity,
            preferred_study_timings=request.context.get("preferred_study_timings", "Evening")
        )
        
        plan_res = await self.service.generate_plan(
            study_req,
            query_override=request.query
        )
        result_json = plan_res.model_dump_json()
        
        return AgentResponse(
            agent_type=AgentType.STUDY_PLANNER,
            result=result_json,
            actions_taken=["calendar_retrieval", "study_plan_generation"],
            metadata=plan_res.metadata
        )

    async def get_memory(self, user_id: str) -> Any:
        return {}
        
    async def run_background_task(self, task_data: Any) -> None:
        pass

# Register the agent
AgentRegistry.register(AgentType.STUDY_PLANNER, StudyPlannerAgent)
