from typing import List
from app.domain.interfaces.chunker import ChunkerInterface
from app.domain.schemas.document import DocumentResponse
from app.core.chunk_config import chunk_config

class FixedSizeChunkSplitter(ChunkerInterface):
    """
    Splits text strictly by a fixed number of characters.
    Prepared to be replaced or wrapped by LangChain's CharacterTextSplitter in the future.
    """
    
    @property
    def strategy_name(self) -> str:
        return "fixed_size"
        
    def split(self, document: DocumentResponse) -> List[str]:
        text = document.content
        size = chunk_config.chunk_size
        overlap = chunk_config.chunk_overlap
        
        chunks = []
        start = 0
        text_length = len(text)
        
        # Guard clause for empty text
        if not text:
            return []
            
        while start < text_length:
            end = start + size
            chunks.append(text[start:end])
            start += (size - overlap)
            
        return chunks
