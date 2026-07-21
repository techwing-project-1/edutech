from fastapi import APIRouter, HTTPException, Depends
from app.domain.schemas.study_notes import StudyNotesRequest, StudyNotesResponse
from app.services.study_notes.manager import StudyNotesManager
from app.core.exceptions import StudyNotesException, StudyNotesValidationError
# Import generator to ensure registry happens
import app.services.study_notes.generator 

router = APIRouter()

# Dependency for manager
def get_manager():
    return StudyNotesManager()

@router.post(
    "/generate", 
    response_model=StudyNotesResponse,
    summary="Generate Study Notes",
    description="Generates AI study notes of various types (Detailed, Exam Revision, etc.) using the Content Generation Engine."
)
async def generate_study_notes(
    request: StudyNotesRequest, 
    manager: StudyNotesManager = Depends(get_manager)
):
    try:
        response = await manager.generate(request)
        return response
    except StudyNotesValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StudyNotesException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
