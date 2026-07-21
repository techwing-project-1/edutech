import time
from datetime import datetime, timezone
from app.domain.schemas.monitoring import HealthResponse, ComponentHealth
from app.infrastructure.opensearch.client import opensearch_manager
from app.core.logger import logger

class HealthMonitor:
    @staticmethod
    def check_health() -> HealthResponse:
        now = datetime.now(timezone.utc).isoformat()
        
        services = {}
        overall_status = "UP"
        
        def mock_check(name: str, version: str) -> ComponentHealth:
            # Helper for internal components that don't need network checks
            return ComponentHealth(status="UP", latency=0.1, version=version, last_check=now)

        # 1. OpenSearch
        try:
            start_time = time.time()
            os_status = opensearch_manager.check_connection()
            latency = (time.time() - start_time) * 1000
            
            if os_status.get("status") in ["green", "yellow"]:
                services["OpenSearch"] = ComponentHealth(status="UP", latency=latency, version="2.x", last_check=now)
            else:
                services["OpenSearch"] = ComponentHealth(status="DEGRADED", latency=latency, version="2.x", last_check=now)
                overall_status = "DEGRADED"
        except Exception as e:
            logger.error(f"Health check failed for OpenSearch: {e}")
            services["OpenSearch"] = ComponentHealth(status="DOWN", latency=0.0, version="unknown", last_check=now)
            overall_status = "DEGRADED"

        # 2. Gemini
        # We assume Gemini is UP unless an active API check is made. 
        services["Gemini"] = mock_check("Gemini", "1.5-flash")
        
        # 3. Router
        services["Router"] = mock_check("Router", "1.0")
        
        # 4. Embedding Service
        services["Embedding Service"] = mock_check("Embedding Service", "SentenceTransformers")
        
        # 5. Provider Registry
        services["Provider Registry"] = mock_check("Provider Registry", "1.0")
        
        # 6. Agent Registry
        services["Agent Registry"] = mock_check("Agent Registry", "1.0")
        
        # 7. Configuration
        services["Configuration"] = mock_check("Configuration", "1.0")
        
        # 8. Feature Flags
        services["Feature Flags"] = mock_check("Feature Flags", "1.0")
        
        # 9. Notification Engine
        services["Notification Engine"] = mock_check("Notification Engine", "1.0")
        
        # 10. Calendar Engine
        services["Calendar Engine"] = mock_check("Calendar Engine", "1.0")
        
        # 11. Planner
        services["Planner"] = mock_check("Planner", "1.0")
        
        # 12. Reminder
        services["Reminder"] = mock_check("Reminder", "1.0")
        
        # 13. Assignment
        services["Assignment"] = mock_check("Assignment", "1.0")
        
        # 14. Quiz
        services["Quiz"] = mock_check("Quiz", "1.0")
        
        # 15. Flashcards
        services["Flashcards"] = mock_check("Flashcards", "1.0")
        
        # 16. Study Notes
        services["Study Notes"] = mock_check("Study Notes", "1.0")
        
        # 17. Summary
        services["Summary"] = mock_check("Summary", "1.0")
        
        return HealthResponse(
            status=overall_status,
            timestamp=now,
            services=services
        )
