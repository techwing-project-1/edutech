from app.domain.schemas.document import DocumentResponse
from app.domain.schemas.chunk import DocumentChunk, ChunkResponse
from app.core.chunk_config import ChunkStrategy, chunk_config
from app.infrastructure.chunkers.factory import ChunkerFactory
from app.services.chunking.metadata import ChunkMetadataGenerator
from app.services.chunking.validator import ChunkValidator
from app.core.logger import logger

class ChunkService:
    """
    Core orchestrator for a single document's chunking lifecycle.
    """
    
    @staticmethod
    def process_document(document: DocumentResponse, strategy: ChunkStrategy = None) -> ChunkResponse:
        active_strategy = strategy or chunk_config.default_strategy
        logger.info(f"Chunking document '{document.metadata.file_name}' using strategy: {active_strategy}")
        
        # 1. Instantiate correct splitter dynamically
        chunker = ChunkerFactory.get_chunker(active_strategy)
        
        # 2. Perform raw text split
        raw_chunks = chunker.split(document)
        
        # 3. Validate integrity
        ChunkValidator.validate(raw_chunks)
        
        # 4. Construct rich chunk models
        document_chunks = []
        total_chunks = len(raw_chunks)
        
        for idx, text in enumerate(raw_chunks):
            # Skip genuinely empty chunks logged during validation
            if not text.strip():
                continue
                
            meta = ChunkMetadataGenerator.generate(
                chunk_index=idx,
                total_chunks=total_chunks,
                parent_metadata=document.metadata,
                strategy=chunker.strategy_name
            )
            document_chunks.append(DocumentChunk(text=text.strip(), metadata=meta))
            
        logger.info(f"Successfully created {len(document_chunks)} chunks for {document.metadata.file_name}.")
        return ChunkResponse(chunks=document_chunks)
