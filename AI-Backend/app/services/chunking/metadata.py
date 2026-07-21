from app.domain.schemas.chunk import ChunkMetadata
from app.domain.schemas.document import DocumentMetadata

class ChunkMetadataGenerator:
    """
    Generates rich metadata for individual chunks.
    Crucial for RAG: Each chunk must remember which document it came from and where it belongs.
    """
    
    @staticmethod
    def generate(chunk_index: int, total_chunks: int, parent_metadata: DocumentMetadata, strategy: str) -> ChunkMetadata:
        return ChunkMetadata(
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            parent_document_metadata=parent_metadata,
            strategy_used=strategy
        )
