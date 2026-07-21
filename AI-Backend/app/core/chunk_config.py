from pydantic import BaseModel
from enum import Enum

class ChunkStrategy(str, Enum):
    FIXED = "fixed"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"

class ChunkConfiguration(BaseModel):
    """
    Configuration for the Smart Text Chunking Layer.
    Controls chunk sizes, overlaps, and default strategies.
    """
    default_strategy: ChunkStrategy = ChunkStrategy.RECURSIVE
    chunk_size: int = 800
    chunk_overlap: int = 150
    
    # Future settings for Semantic Chunking
    semantic_threshold: float = 0.75

chunk_config = ChunkConfiguration()
