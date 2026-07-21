from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.agent import AgentRequest, AgentResponse
from app.agents.manager import AgentManager
from app.core.exceptions import AgentException, AgentValidationError

router = APIRouter()

# Dependency for manager
def get_manager():
    return AgentManager()

@router.post(
    "/orchestrate", 
    response_model=AgentResponse,
    summary="Orchestrate Educational Agent",
    description="Routes the query to the correct OpenClaw agent."
)
async def orchestrate_agent(
    request: AgentRequest, 
    manager: AgentManager = Depends(get_manager)
):
    try:
        response = await manager.orchestrate(request)
        return response
    except AgentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AgentException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
