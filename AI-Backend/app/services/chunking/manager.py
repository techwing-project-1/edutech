from typing import List
from app.domain.schemas.document import DocumentResponse
from app.domain.schemas.chunk import ChunkResponse
from app.services.chunking.service import ChunkService
from app.core.chunk_config import ChunkStrategy
from app.core.logger import logger

class ChunkManager:
    """
    High-level facade for the entire Chunking Layer.
    Exposes single and batch processing capabilities to the Application layer.
    """
    
    @staticmethod
    def process_single(document: DocumentResponse, strategy: ChunkStrategy = None) -> ChunkResponse:
        """Process a single document."""
        return ChunkService.process_document(document, strategy)

    @staticmethod
    def process_batch(documents: List[DocumentResponse], strategy: ChunkStrategy = None) -> List[ChunkResponse]:
        """Process multiple documents sequentially or concurrently."""
        logger.info(f"Starting batch chunking for {len(documents)} documents.")
        responses = []
        for doc in documents:
            responses.append(ChunkService.process_document(doc, strategy))
        return responses
