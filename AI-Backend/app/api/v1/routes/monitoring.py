from fastapi import APIRouter
from app.domain.schemas.monitoring import HealthResponse, OverallStatistics, MonitoringDataResponse, PerformanceResponse
from app.monitoring.monitor import AIMonitor

router = APIRouter()

@router.get("/health", response_model=HealthResponse, summary="Get API Health")
def get_health():
    return AIMonitor.get_health()

@router.get("/statistics", response_model=OverallStatistics, summary="Get Overall Statistics")
def get_statistics():
    return AIMonitor.get_statistics()

@router.get("/providers", response_model=MonitoringDataResponse, summary="Get Provider Stats")
def get_providers():
    return MonitoringDataResponse(data=AIMonitor.get_providers_stats())

@router.get("/agents", response_model=MonitoringDataResponse, summary="Get Agent Stats")
def get_agents():
    return MonitoringDataResponse(data=AIMonitor.get_agents_stats())

@router.get("/performance", response_model=PerformanceResponse, summary="Get API Performance")
def get_performance():
    return AIMonitor.get_performance()
