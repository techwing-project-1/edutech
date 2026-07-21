from app.domain.schemas.rag import RAGRequest, RAGResponse
from app.services.rag.service import RAGService

class RAGManager:
    """
    High-level Orchestrator / Facade for the RAG Engine.
    """
    
    @staticmethod
    async def query(request: RAGRequest) -> RAGResponse:
        service = RAGService()
        return await service.execute_query(request)
