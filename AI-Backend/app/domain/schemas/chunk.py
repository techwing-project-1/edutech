from pydantic import BaseModel, Field
from typing import List
from app.domain.schemas.document import DocumentMetadata

class ChunkMetadata(BaseModel):
    """
    Metadata associated with a single text chunk.
    Retains parent document context, which is critical for accurate retrieval in RAG.
    """
    chunk_index: int = Field(..., description="The sequential index of this chunk in the document.")
    total_chunks: int = Field(..., description="Total number of chunks the document was split into.")
    parent_document_metadata: DocumentMetadata = Field(..., description="Metadata of the original document.")
    strategy_used: str = Field(..., description="The chunking strategy applied (e.g., recursive, fixed).")

class DocumentChunk(BaseModel):
    """
    Standardized Chunk Model. 
    Designed to perfectly align with LangChain's Document schema for the upcoming Embeddings Layer.
    """
    text: str = Field(..., description="The actual text content of the chunk.")
    metadata: ChunkMetadata = Field(..., description="Rich metadata tracking origin and position.")

class ChunkResponse(BaseModel):
    """
    Response model containing all chunks for a single document.
    """
    chunks: List[DocumentChunk] = Field(default_factory=list)
