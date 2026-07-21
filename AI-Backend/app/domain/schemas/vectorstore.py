from pydantic import BaseModel, Field
from typing import List, Optional

class VectorMetadata(BaseModel):
    """
    Strict Metadata Schema for Vector Database records.
    Ensures all metadata fields are validated before OpenSearch insertion.
    """
    document_id: str
    document_name: str
    department: str
    subject: str
    semester: int
    section: str
    faculty_name: str
    page_number: int
    chunk_id: str
    chunk_index: int
    embedding_model: str
    created_at: str
    upload_time: str
    source_file_type: str

class VectorRecord(BaseModel):
    """
    Represents a complete record ready for insertion into the Vector Store.
    """
    id: str = Field(..., description="Unique ID for the chunk (e.g., document_id_chunk_index)")
    embedding: List[float] = Field(..., description="Numerical embedding vector from the Embedding Layer")
    metadata: VectorMetadata = Field(..., description="Rich metadata for precise filtering and RAG retrieval")
    document_text: str = Field(..., description="The actual raw text content corresponding to the embedding")

class SearchResult(BaseModel):
    """
    Represents a single match from a similarity search.
    """
    id: str
    score: float
    document_text: str
    metadata: VectorMetadata

class VectorSearchResponse(BaseModel):
    """
    Standardized response containing all Top-K matches.
    """
    results: List[SearchResult] = Field(default_factory=list)

class CollectionStats(BaseModel):
    """
    Provides statistics about a specific collection.
    """
    collection_name: str
    total_vectors: int
