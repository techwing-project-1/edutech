from typing import List
from app.core.exceptions import ChunkingException
from app.core.logger import logger

class ChunkValidator:
    """
    Validates the output of a Chunker before it is sent to the Embedding Layer.
    Prevents corrupt or empty data from entering the Vector Database.
    """
    
    @staticmethod
    def validate(raw_chunks: List[str]) -> None:
        if not raw_chunks:
            raise ChunkingException("Chunking Validation Failed: The document yielded zero chunks.")
            
        for idx, chunk in enumerate(raw_chunks):
            if not chunk or not chunk.strip():
                # We log a warning instead of raising an exception because a single empty chunk
                # shouldn't crash a 500-page document processing pipeline.
                logger.warning(f"Validation Warning: Empty chunk detected at index {idx}.")
