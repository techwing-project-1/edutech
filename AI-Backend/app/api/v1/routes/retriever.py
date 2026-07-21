from fastapi import APIRouter, HTTPException
from app.domain.schemas.retriever import RetrieverRequest, RetrieverResponse
from app.services.retriever.manager import RetrieverManager
from app.core.logger import logger

router = APIRouter()
manager = RetrieverManager()

@router.post("/search", response_model=RetrieverResponse)
async def search_context(request: RetrieverRequest):
    """
    Execute semantic similarity search against the Vector Database.
    Applies strict metadata filtering if provided (Department, Semester, Subject, etc.).
    Returns context chunks ready for RAG ingestion.
    """
    try:
        return await manager.search(request)
    except Exception as e:
        logger.error(f"Retriever API endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
