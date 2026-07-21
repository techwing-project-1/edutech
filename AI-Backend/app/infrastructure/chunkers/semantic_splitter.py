from typing import List
from app.domain.interfaces.chunker import ChunkerInterface
from app.domain.schemas.document import DocumentResponse
from app.core.exceptions import ChunkingException

class SemanticChunkSplitter(ChunkerInterface):
    """
    Placeholder for future Semantic Chunking.
    Will chunk text based on meaning boundaries (using small embedding models) rather than character counts.
    """
    
    @property
    def strategy_name(self) -> str:
        return "semantic"
        
    def split(self, document: DocumentResponse) -> List[str]:
        raise ChunkingException("Semantic Chunk Splitter is a future roadmap item and is not yet implemented.")
