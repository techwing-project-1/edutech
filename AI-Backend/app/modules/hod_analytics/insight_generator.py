import json
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.domain.schemas.llm import LLMRequest
from app.modules.hod_analytics.request_models import HODAnalyticsRequest
from app.modules.hod_analytics.response_models import HODAnalysisResponse
from app.modules.hod_analytics.risk_analyzer import RiskAnalyzer
from app.modules.hod_analytics.trend_analyzer import TrendAnalyzer

class InsightGenerator:
    """Constructs prompts and uses LLMManager to generate overall department summaries."""
    
    def __init__(self):
        self.llm_manager = LLMManager()
        
    async def generate_insights(self, request: HODAnalyticsRequest) -> HODAnalysisResponse:
        data = request.data
        
        # Combine base data with specialized analyzer prompts
        risk_prompt = RiskAnalyzer.generate_risk_prompt(data)
        trend_prompt = TrendAnalyzer.generate_trend_prompt(data)
        
        system_prompt = (
            "You are an AI Analytics Expert for a University Head of Department (HOD).\n"
            "Generate a comprehensive analysis of the department based on the provided metrics.\n"
            "Return ONLY valid JSON matching this schema:\n"
            '{"summary": "...", "key_findings": ["..."], "strengths": ["..."], "weaknesses": ["..."], "risk_areas": ["..."], "recommendations": ["..."], "priority_actions": [{"action": "...", "impact": "..."}], "overall_health_score": 85.5}'
        )
        
        user_prompt = (
            f"Department: {data.department_name}, Semester: {data.semester}\n"
            f"{risk_prompt}\n\n{trend_prompt}\n\n"
            "Provide a holistic department overview, identifying key findings, strengths, weaknesses, and a health score."
        )
        
        llm_req = LLMRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=2500
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
            raise HODLLMException(f"Failed to parse LLM insights: {str(e)}")
