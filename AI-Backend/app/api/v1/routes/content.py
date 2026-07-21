from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.content_generation import ContentGenerationRequest, ContentGenerationResponse
from app.services.content_generation.manager import ContentGenerationManager
from app.core.exceptions import (
    ContentGenerationError, 
    ContentValidationError,
    EmptyContextError,
    UnsupportedGenerationModeError,
    ProviderError
)

router = APIRouter()

# Dependency for manager
def get_manager():
    return ContentGenerationManager()

@router.post(
    "/generate", 
    response_model=ContentGenerationResponse,
    summary="Generate Educational Content",
    description="Generates AI content (Summary, Flashcards, Quiz, etc.) using RAG context and LLM."
)
async def generate_content(
    request: ContentGenerationRequest, 
    manager: ContentGenerationManager = Depends(get_manager)
):
    try:
        response = await manager.generate_content(request)
        return response
    except ContentValidationError as e:
        raise HTTPException(status_code=422, detail=str(e.message))
    except UnsupportedGenerationModeError:
        raise HTTPException(status_code=400, detail="Unsupported generation mode")
    except EmptyContextError:
        raise HTTPException(status_code=404, detail="No relevant context found.")
    except ProviderError:
        raise HTTPException(status_code=503, detail="LLM Provider Error")
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
