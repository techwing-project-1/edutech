from fastapi import APIRouter, HTTPException
from app.domain.schemas.rag import RAGRequest, RAGResponse
from app.services.rag.manager import RAGManager
from app.core.logger import logger

router = APIRouter()

@router.post("/query", response_model=RAGResponse)
async def ask_question(request: RAGRequest):
    """
    Execute a full Retrieval-Augmented Generation (RAG) query.
    Takes a user question, retrieves relevant context from ChromaDB, limits token sizes, 
    compiles templates via the Prompt Builder, and streams the prompt to Gemini (or OpenRouter on failure).
    Returns the Answer + Metadata Sources + Latency.
    """
    try:
        return await RAGManager.query(request)
    except Exception as e:
        logger.error(f"RAG Endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
