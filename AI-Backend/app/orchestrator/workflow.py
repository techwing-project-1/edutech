import uuid
import asyncio
import time
from app.domain.schemas.orchestrator import OrchestratorRequest, NormalizedResponse, AIMode
from app.orchestrator.selector import AIModeSelector
from app.orchestrator.router import RequestRouter
from app.orchestrator.aggregator import ResponseAggregator
from app.core.exceptions import OrchestratorValidationError
from app.core.logger import logger

class WorkflowManager:
    """Manages the lifecycle of an AI request: Mode Selection -> Routing -> Execution -> Aggregation"""
    
    @staticmethod
    async def execute(request: OrchestratorRequest) -> NormalizedResponse:
        exec_id = str(uuid.uuid4())
        logger.info(f"Orchestrator Execution {exec_id} started for user {request.user_id}")
        
        mode = AIModeSelector.detect_mode(request)
        start_time = time.time()
        
        try:
            logger.info(f"Execution {exec_id}: Mode detected as {mode}")
            
            # Execute with a 30s timeout enforcing strict SLA
            raw_response = await asyncio.wait_for(RequestRouter.route(mode, request), timeout=30.0)
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"Execution {exec_id} completed successfully.",
                extra={
                    "extra_info": {
                        "execution_id": exec_id,
                        "user_id": request.user_id,
                        "mode": mode.value,
                        "status": "SUCCESS",
                        "latency_ms": execution_time
                    }
                }
            )
            
            return ResponseAggregator.aggregate(
                execution_id=exec_id,
                mode=mode,
                success=True,
                raw_data=raw_response,
                execution_time=execution_time
            )
            
        except asyncio.TimeoutError:
            execution_time = (time.time() - start_time) * 1000
            logger.error(
                f"Execution {exec_id} timed out.",
                extra={
                    "extra_info": {
                        "execution_id": exec_id,
                        "user_id": request.user_id,
                        "mode": mode.value,
                        "status": "TIMEOUT",
                        "latency_ms": execution_time,
                        "errors": 1
                    }
                }
            )
            return ResponseAggregator.aggregate(
                execution_id=exec_id,
                mode=mode,
                success=False,
                raw_data=None,
                error="Execution timed out after 30 seconds",
                execution_time=execution_time
            )
        except OrchestratorValidationError:
            raise  # Let the API layer catch this and return HTTP 400
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(
                f"Execution {exec_id} failed: {e}",
                extra={
                    "extra_info": {
                        "execution_id": exec_id,
                        "user_id": request.user_id,
                        "mode": mode.value,
                        "status": "FAILED",
                        "latency_ms": execution_time,
                        "errors": 1
                    }
                }
            )
            return ResponseAggregator.aggregate(
                execution_id=exec_id,
                mode=mode,
                success=False,
                raw_data=None,
                error=str(e),
                execution_time=execution_time
            )
