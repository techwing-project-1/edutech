from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.flashcards import FlashcardRequest, FlashcardResponse
from app.services.flashcards.manager import FlashcardManager
from app.core.exceptions import FlashcardException, FlashcardValidationError, EmptyContextError, LLMReturnedInvalidJSON

router = APIRouter()

# Dependency for manager
def get_manager():
    return FlashcardManager()

@router.post(
    "/generate", 
    response_model=FlashcardResponse,
    summary="Generate Structured Flashcards",
    description="Generates AI flashcards in a structured JSON array format, using the Content Generation Engine."
)
async def generate_flashcards(
    request: FlashcardRequest, 
    manager: FlashcardManager = Depends(get_manager)
):
    try:
        response = await manager.generate(request)
        return response
    except FlashcardValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EmptyContextError:
        raise HTTPException(status_code=404, detail="No relevant context found.")
    except LLMReturnedInvalidJSON as e:
        raise HTTPException(status_code=422, detail=f"LLM generated invalid JSON format: {str(e)}")
    except FlashcardException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
