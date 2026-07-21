from app.domain.interfaces.chunker import ChunkerInterface
from app.core.chunk_config import ChunkStrategy
from app.infrastructure.chunkers.fixed_splitter import FixedSizeChunkSplitter
from app.infrastructure.chunkers.recursive_splitter import RecursiveTextSplitter
from app.infrastructure.chunkers.semantic_splitter import SemanticChunkSplitter
from app.core.exceptions import ChunkingException

class ChunkerFactory:
    """
    Factory Pattern for dynamically instantiating chunking strategies.
    Ensures the service layer relies entirely on abstractions.
    """
    
    @staticmethod
    def get_chunker(strategy: ChunkStrategy) -> ChunkerInterface:
        if strategy == ChunkStrategy.FIXED:
            return FixedSizeChunkSplitter()
        elif strategy == ChunkStrategy.RECURSIVE:
            return RecursiveTextSplitter()
        elif strategy == ChunkStrategy.SEMANTIC:
            return SemanticChunkSplitter()
        else:
            raise ChunkingException(f"Unsupported chunking strategy: {strategy}")
