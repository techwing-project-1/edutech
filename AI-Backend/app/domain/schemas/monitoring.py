from pydantic import BaseModel
from typing import Dict, Any

class ComponentHealth(BaseModel):
    status: str
    latency: float
    version: str
    last_check: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, ComponentHealth]

class AgentStats(BaseModel):
    agent_name: str
    status: str
    registered: bool
    version: str
    current_requests: int
    total_calls: int = 0
    success_rate: float = 0.0
    average_latency_ms: float = 0.0
    last_execution: str
    supported_modes: list[str]
    timeout_seconds: float
    queue_size: int
    errors: int = 0

class ProviderStats(BaseModel):
    provider_name: str
    status: str
    is_primary: bool
    is_fallback: bool
    model: str
    timeout_seconds: float
    retry_count: int
    total_requests: int = 0
    total_tokens: int = 0
    fallback_count: int = 0
    quota_errors: int = 0
    average_latency_ms: float = 0.0
    availability_percentage: float = 100.0

class OverallStatistics(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    failure_rate: float
    average_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    median_latency_ms: float
    p90_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    average_token_usage: float
    opensearch_query_time_ms: float
    gemini_response_time_ms: float
    agent_execution_time_ms: float
    memory_usage_mb: float
    peak_memory_mb: float
    cpu_usage_percent: float
    concurrent_requests: int
    uptime_seconds: int

class MonitoringDataResponse(BaseModel):
    data: Dict[str, Any]

class PerformanceResponse(BaseModel):
    current_active_provider: str
    fallback_provider: str
    total_gemini_requests: int
    total_openrouter_requests: int
    gemini_success: int
    gemini_failures: int
    gemini_quota_errors: int
    openrouter_success: int
    openrouter_failures: int
    fallback_count: int
    fallback_success_rate: float
    average_gemini_latency_ms: float
    average_openrouter_latency_ms: float
    provider_health: str
    circuit_breaker_status: str
