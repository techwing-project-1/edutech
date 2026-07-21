from app.domain.schemas.monitoring import HealthResponse, OverallStatistics
from app.monitoring.health import HealthMonitor
from app.monitoring.statistics import StatisticsService

class AIMonitor:
    """Facade for the AI Monitoring Layer"""
    
    @staticmethod
    def get_health() -> HealthResponse:
        return HealthMonitor.check_health()
        
    @staticmethod
    def get_statistics() -> OverallStatistics:
        return StatisticsService.get_overall()
        
    @staticmethod
    def get_agents_stats() -> dict:
        return StatisticsService.get_agents()
        
    @staticmethod
    def get_providers_stats() -> dict:
        return StatisticsService.get_providers()
