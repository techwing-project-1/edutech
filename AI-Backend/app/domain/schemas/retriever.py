from pydantic import BaseModel, Field
from typing import List, Optional
from app.domain.schemas.vectorstore import VectorMetadata

class RetrieverRequest(BaseModel):
    """
    Request model for executing a semantic search across the knowledge base.
    """
    query: str = Field(..., description="The user's raw question")
    
    # Metadata Filters
    document_id: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    subject: Optional[str] = None
    section: Optional[str] = None
    faculty_name: Optional[str] = None
    
    # Configuration
    top_k: int = Field(default=5, description="Number of chunks to retrieve")
    similarity_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum similarity score")
    explain_mode: bool = Field(default=False, description="Enable debug logging of raw queries")

class RetrievedChunk(BaseModel):
    """
    A single matched chunk retrieved from the Vector Store.
    """
    id: str = Field(alias="chunk_id")
    text: str
    score: float
    confidence: str
    document_name: Optional[str] = None
    page: Optional[int] = None
    metadata: VectorMetadata

class RetrieverResponse(BaseModel):
    """
    Standardized response containing all Top-K retrieved context chunks.
    """
    status: str = "success"
    query: str
    retrieval_time_ms: int
    threshold_used: float
    filters: dict
    retrieved_chunk_count: int
    chunks: List[RetrievedChunk] = Field(default_factory=list)
