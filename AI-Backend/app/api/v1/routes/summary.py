from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.summary import SummaryRequest, SummaryResponse
from app.services.summary.manager import SummaryManager
from app.core.exceptions import SummaryException, SummaryValidationError

router = APIRouter()

# Dependency for manager
def get_manager():
    return SummaryManager()

@router.post(
    "/generate", 
    response_model=SummaryResponse,
    summary="Generate a Summary",
    description="Generates AI summaries of various types (Short, Detailed, Bullet Point, etc.) using the Content Generation Engine."
)
async def generate_summary(
    request: SummaryRequest, 
    manager: SummaryManager = Depends(get_manager)
):
    try:
        response = await manager.generate(request)
        return response
    except SummaryValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SummaryException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
