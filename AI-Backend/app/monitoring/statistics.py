import time
from app.domain.schemas.monitoring import OverallStatistics, AgentStats, ProviderStats
from app.monitoring.metrics import metrics_collector

class StatisticsService:
    @staticmethod
    def get_overall() -> OverallStatistics:
        uptime = int(time.time() - metrics_collector.start_time)
        
        with metrics_collector.lock:
            total_reqs = metrics_collector.total_requests
            failed_reqs = metrics_collector.total_errors
            concurrent = metrics_collector.concurrent_requests
            total_tokens = metrics_collector.total_tokens
            
        success_reqs = total_reqs - failed_reqs
        
        success_rate = 0.0
        failure_rate = 0.0
        if total_reqs > 0:
            success_rate = (success_reqs / total_reqs) * 100.0
            failure_rate = (failed_reqs / total_reqs) * 100.0
            
        avg_latency = metrics_collector.get_avg_metric(metrics_collector.latency_window)
        latencies = metrics_collector.get_overall_latencies()
        
        avg_opensearch = metrics_collector.get_avg_metric(metrics_collector.opensearch_latency_window)
        avg_gemini = metrics_collector.get_avg_metric(metrics_collector.gemini_latency_window)
        avg_agent = metrics_collector.get_avg_metric(metrics_collector.agent_execution_latency_window)
            
        import psutil
        import os
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        memory_usage = mem_info.rss / (1024 * 1024) # MB
        peak_memory = getattr(mem_info, 'peak_wset', mem_info.rss) / (1024 * 1024)
        cpu_usage = psutil.cpu_percent(interval=0.0) # non-blocking after first call
            
        return OverallStatistics(
            total_requests=total_reqs,
            successful_requests=success_reqs,
            failed_requests=failed_reqs,
            success_rate=success_rate,
            failure_rate=failure_rate,
            average_latency_ms=avg_latency,
            min_latency_ms=latencies["min"],
            max_latency_ms=latencies["max"],
            median_latency_ms=latencies["median"],
            p90_latency_ms=latencies["p90"],
            p95_latency_ms=latencies["p95"],
            p99_latency_ms=latencies["p99"],
            average_token_usage=(total_tokens / total_reqs) if total_reqs > 0 else 0.0,
            opensearch_query_time_ms=avg_opensearch,
            gemini_response_time_ms=avg_gemini,
            agent_execution_time_ms=avg_agent,
            memory_usage_mb=memory_usage,
            peak_memory_mb=peak_memory,
            cpu_usage_percent=cpu_usage,
            concurrent_requests=concurrent,
            uptime_seconds=uptime
        )
        
    @staticmethod
    def get_agents() -> dict:
        result = {}
        now = time.time()
        from datetime import datetime, timezone
        
        for name, data in metrics_collector.agents.items():
            calls = data["calls"]
            errors = data["errors"]
            sr = 0.0
            if calls > 0:
                sr = ((calls - errors) / calls) * 100
                
            avg_lat = 0.0
            if calls > 0:
                avg_lat = data["latency"] / calls
                
            result[name] = AgentStats(
                agent_name=name,
                status="ACTIVE" if calls > 0 else "IDLE",
                registered=True,
                version="1.0",
                current_requests=0, # In a real system, we would track in-flight requests
                total_calls=calls,
                success_rate=sr,
                average_latency_ms=avg_lat,
                last_execution=datetime.now(timezone.utc).isoformat(),
                supported_modes=[name.upper()],
                timeout_seconds=30.0,
                queue_size=0,
                errors=errors
            ).model_dump()
            
        if not result:
            # Register defaults if empty
            for name in ["calendar", "assignment", "study_planner", "reminder"]:
                result[name] = AgentStats(
                    agent_name=name,
                    status="IDLE",
                    registered=True,
                    version="1.0",
                    current_requests=0,
                    total_calls=0,
                    last_execution=datetime.now(timezone.utc).isoformat(),
                    supported_modes=[name.upper()],
                    timeout_seconds=30.0,
                    queue_size=0
                ).model_dump()
                
        return result
        
    @staticmethod
    def get_providers() -> dict:
        result = {}
        for name, data in metrics_collector.providers.items():
            reqs = data["requests"]
            avg_lat = 0.0
            if reqs > 0:
                avg_lat = data["latency"] / reqs
                
            availability = 100.0
            if reqs > 0:
                availability = ((reqs - data.get("errors", 0)) / reqs) * 100
                
            is_primary = (name.lower() == "gemini")
                
            result[name] = ProviderStats(
                provider_name=name,
                status="ACTIVE",
                is_primary=is_primary,
                is_fallback=not is_primary,
                model="gemini-1.5-flash" if is_primary else "openrouter/auto",
                timeout_seconds=30.0,
                retry_count=data.get("errors", 0),
                total_requests=reqs,
                total_tokens=data["tokens"],
                fallback_count=data["fallbacks"],
                average_latency_ms=avg_lat,
                availability_percentage=availability
            ).model_dump()
        
        # If empty, return at least the registered defaults
        if not result:
            result["gemini"] = ProviderStats(
                provider_name="gemini",
                status="ACTIVE",
                is_primary=True,
                is_fallback=False,
                model="gemini-1.5-flash",
                timeout_seconds=30.0,
                retry_count=0
            ).model_dump()
            result["openrouter"] = ProviderStats(
                provider_name="openrouter",
                status="STANDBY",
                is_primary=False,
                is_fallback=True,
                model="openrouter/auto",
                timeout_seconds=30.0,
                retry_count=0
            ).model_dump()
            
        return result

    @staticmethod
    def get_performance() -> dict:
        from app.domain.schemas.monitoring import PerformanceResponse
        from app.core.config import settings
        
        providers = StatisticsService.get_providers()
        gemini = providers.get("gemini", {})
        openrouter = providers.get("openrouter", {})
        
        fallback_count = openrouter.get("fallback_count", 0)
        openrouter_reqs = openrouter.get("total_requests", 0)
        openrouter_errs = openrouter.get("retry_count", 0) # errors field is mapped to retry_count in ProviderStats dict
        
        fallback_success = 0.0
        if fallback_count > 0:
            # simple approximation: if openrouter succeeded, fallback succeeded
            fallback_success = max(0.0, ((openrouter_reqs - openrouter_errs) / openrouter_reqs) * 100) if openrouter_reqs > 0 else 0.0
            
        return PerformanceResponse(
            current_active_provider=getattr(settings, "PRIMARY_PROVIDER", "gemini"),
            fallback_provider=getattr(settings, "FALLBACK_PROVIDER", "openrouter"),
            total_gemini_requests=gemini.get("total_requests", 0),
            total_openrouter_requests=openrouter_reqs,
            gemini_success=gemini.get("total_requests", 0) - gemini.get("retry_count", 0),
            gemini_failures=gemini.get("retry_count", 0),
            gemini_quota_errors=gemini.get("quota_errors", 0),
            openrouter_success=openrouter_reqs - openrouter_errs,
            openrouter_failures=openrouter_errs,
            fallback_count=fallback_count,
            fallback_success_rate=fallback_success,
            average_gemini_latency_ms=gemini.get("average_latency_ms", 0.0),
            average_openrouter_latency_ms=openrouter.get("average_latency_ms", 0.0),
            provider_health="UP", # will be accurate via Health API
            circuit_breaker_status="CLOSED"
        ).model_dump()
