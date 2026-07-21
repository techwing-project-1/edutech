from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.pipeline.indexing_pipeline import IndexingPipeline, IndexingStatus
from app.core.logger import logger

router = APIRouter()

@router.post("/index", response_model=IndexingStatus)
async def index_document(
    file: UploadFile = File(...),
    document_id: Optional[str] = Form(None, description="Optional unique ID for the document."),
    faculty_name: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    semester: Optional[int] = Form(None),
    section: Optional[str] = Form(None)
):
    """
    API Endpoint to execute the complete PDF Indexing Pipeline.
    Uploads the file, extracts text, chunks it, generates embeddings, and stores it in OpenSearch.
    """
    try:
        pipeline = IndexingPipeline()
        result = await pipeline.execute(
            file=file,
            document_id=document_id,
            faculty_name=faculty_name,
            department=department,
            subject=subject,
            semester=semester,
            section=section
        )
        return result
    except Exception as e:
        logger.error(f"Endpoint /index failed: {str(e)}")
        # Check if the error is already our custom processing exception
        stage = getattr(e, "stage", "pipeline_execution")
        status_code = getattr(e, "status_code", 500)
        
        raise HTTPException(
            status_code=status_code, 
            detail={
                "success": False,
                "message": "Document indexing failed.",
                "error": str(e),
                "stage": stage
            }
        )
