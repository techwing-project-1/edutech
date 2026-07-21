from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.domain.schemas.quiz import QuizRequest, QuizResponse
from app.services.quiz.manager import QuizManager
from app.core.exceptions import QuizException, QuizValidationError

router = APIRouter()

# Dependency for manager
def get_manager():
    return QuizManager()

@router.post(
    "/generate", 
    response_model=QuizResponse,
    summary="Generate Structured Quiz",
    description="Generates AI quizzes in a structured JSON array format, using the Content Generation Engine."
)
async def generate_quiz(
    request: QuizRequest, 
    manager: QuizManager = Depends(get_manager)
):
    try:
        response = await manager.generate(request)
        return response
    except QuizValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except QuizException as e:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": str(e),
                "retry_attempts": 0
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Internal Server Error: {str(e)}",
                "retry_attempts": 0
            }
        )
