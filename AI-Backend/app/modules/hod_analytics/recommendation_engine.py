import json
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.domain.schemas.llm import LLMRequest
from app.modules.hod_analytics.request_models import HODAnalyticsRequest
from app.modules.hod_analytics.response_models import HODAnalysisResponse

class RecommendationEngine:
    """Generates actionable recommendations and priority actions for the HOD."""
    
    def __init__(self):
        self.llm_manager = LLMManager()
        
    async def generate_recommendations(self, request: HODAnalyticsRequest) -> HODAnalysisResponse:
        data = request.data
        system_prompt = (
            "You are an AI Analytics Expert for a University Head of Department (HOD).\n"
            "Generate recommendations based on department data.\n"
            "Return ONLY valid JSON matching this schema:\n"
            '{"summary": "...", "key_findings": ["..."], "strengths": ["..."], "weaknesses": ["..."], "risk_areas": ["..."], "recommendations": ["..."], "priority_actions": [{"action": "...", "impact": "..."}], "overall_health_score": 85.5}'
        )
        
        user_prompt = (
            f"Department: {data.department_name}, Semester: {data.semester}\n"
            f"Students: {data.student_count}, At Risk: {data.at_risk_students_count}\n"
            f"Attendance: {data.attendance_percentage}%, Assignments: {data.assignment_completion_rate}%\n"
            f"Average Marks: {data.average_marks}%\n"
            "Focus exclusively on generating highly actionable Recommendations and Priority Actions to improve department health."
        )
        
        llm_req = LLMRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=2000
        )
        
        response = await self.llm_manager.generate_response(llm_req)
        
        try:
            raw = extract_text(response).strip()
            if raw.startswith("```json"): raw = raw[7:-3]
            elif raw.startswith("```"): raw = raw[3:-3]
            
            parsed = json.loads(raw)
            return HODAnalysisResponse(
                **parsed,
                metadata={"provider_used": response.provider_used, "model_used": response.model_name}
            )
        except Exception as e:
            from app.modules.hod_analytics.exceptions import HODLLMException
            raise HODLLMException(f"Failed to parse LLM recommendations: {str(e)}")
