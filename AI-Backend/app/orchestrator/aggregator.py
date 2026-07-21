from typing import Any, Dict
from datetime import datetime, timezone
from app.domain.schemas.orchestrator import NormalizedResponse, AIMode

class ResponseAggregator:
    """Normalizes diverse responses from internal services into a unified DTO for Spring Boot."""
    
    @staticmethod
    def aggregate(execution_id: str, mode: AIMode, success: bool, raw_data: Any, error: str = None, execution_time: float = 0.0) -> NormalizedResponse:
        
        data_dict = {}
        if raw_data:
            if hasattr(raw_data, "model_dump"):
                data_dict = raw_data.model_dump()
            elif isinstance(raw_data, dict):
                data_dict = raw_data
            else:
                data_dict = {"raw": str(raw_data)}
                
        # Determine appropriate message
        msg = "Execution successful" if success else "Execution failed"
                
        return NormalizedResponse(
            success=success,
            message=msg,
            data=data_dict,
            metadata={
                "mode_executed": mode.value if mode else "UNKNOWN"
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=execution_id,
            execution_time=execution_time,
            error=error
        )
