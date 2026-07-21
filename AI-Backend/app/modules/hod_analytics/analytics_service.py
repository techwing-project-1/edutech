from app.modules.hod_analytics.request_models import HODAnalyticsRequest
from app.modules.hod_analytics.response_models import HODAnalysisResponse
from app.modules.hod_analytics.validators import HODValidator
from app.modules.hod_analytics.insight_generator import InsightGenerator
from app.modules.hod_analytics.report_generator import ReportGenerator
from app.modules.hod_analytics.recommendation_engine import RecommendationEngine

class HODAnalyticsService:
    """Service layer facade orchestrating calls to the generators and analyzers."""
    
    def __init__(self):
        self.insight_generator = InsightGenerator()
        self.report_generator = ReportGenerator()
        self.recommendation_engine = RecommendationEngine()
        
    async def analyze(self, request: HODAnalyticsRequest) -> HODAnalysisResponse:
        HODValidator.validate_request(request)
        return await self.insight_generator.generate_insights(request)
        
    async def generate_report(self, request: HODAnalyticsRequest) -> HODAnalysisResponse:
        HODValidator.validate_request(request)
        return await self.report_generator.generate_report(request)
        
    async def generate_recommendations(self, request: HODAnalyticsRequest) -> HODAnalysisResponse:
        HODValidator.validate_request(request)
        return await self.recommendation_engine.generate_recommendations(request)
