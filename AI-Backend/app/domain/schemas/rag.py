from pydantic import BaseModel, Field
from typing import List, Optional

class RAGSource(BaseModel):
    """Structured representation of a source chunk."""
    document_name: str
    page_number: int
    chunk_id: str
    similarity_score: float
    confidence: str

class RAGRequest(BaseModel):
    """
    Client request schema for triggering the complete RAG Engine.
    """
    query: str = Field(..., description="The user's input question")
    document_id: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    subject: Optional[str] = None
    section: Optional[str] = None
    top_k: int = Field(5, description="Number of context chunks to retrieve")

class RAGResponse(BaseModel):
    """
    Standardized response returned to the client from the RAG Engine.
    Contains the final LLM text, and the structured sources used to generate it.
    """
    answer: str
    sources: List[RAGSource]
    retrieved_chunks: int
    llm_provider: str
    model: str
    success: bool = True
    latency_ms: Optional[int] = None
    average_similarity: float = 0.0
