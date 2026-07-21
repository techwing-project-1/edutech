from app.domain.schemas.agent import AgentRequest, AgentResponse
from app.agents.factory import AgentFactory
from app.agents.validator import AgentValidator
from app.core.exceptions import AgentException, AgentValidationError, EmptyContextError
from app.core.logger import logger

class AgentManager:
    """
    Orchestration layer for OpenClaw Agents.
    Routes requests to the appropriate intelligent agent.
    Reuses Prompt Layer, Provider Layer, General AI, and Course RAG underneath via the selected Agent.
    """

    async def orchestrate(self, request: AgentRequest) -> AgentResponse:
        """
        Validates and orchestrates the agent execution.
        """
        logger.info(f"AgentManager orchestrating {request.agent_type} for user {request.user_id}")
        
        import time
        from app.monitoring.metrics import metrics_collector, ExecutionLogger
        
        start_time = time.time()
        success = True
        try:
            # 1. Validate
            AgentValidator.validate_request(request)
            
            # 2. Instantiate Agent via Factory
            agent = AgentFactory.create_agent(request.agent_type)
            
            # 3. Execute
            response = await agent.execute(request)
            
            return response
            
        except EmptyContextError as e:
            success = False
            logger.warning(f"Empty context for {request.agent_type}: {str(e)}")
            return AgentResponse(
                agent_type=request.agent_type,
                result="No relevant syllabus content found.",
                actions_taken=[],
                metadata={"error": "EmptyContextError"}
            )
        except AgentValidationError as e:
            success = False
            logger.error(f"Agent validation failed: {str(e)}")
            raise e
        except Exception as e:
            success = False
            logger.error(f"Agent execution failed: {str(e)}")
            raise AgentException(f"Failed to execute agent: {str(e)}")
        finally:
            latency_ms = (time.time() - start_time) * 1000
            from app.monitoring.metrics import record_agent_metrics
            record_agent_metrics(request.agent_type.value, latency_ms, success)
            ExecutionLogger.log_execution("AGENT", request.agent_type.value, success, latency_ms)
