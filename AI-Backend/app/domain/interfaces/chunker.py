from abc import ABC, abstractmethod
from typing import List
from app.domain.schemas.document import DocumentResponse

class ChunkerInterface(ABC):
    """
    Base Provider Interface for Text Splitters.
    Follows Strategy Pattern, allowing seamless addition of new chunking algorithms.
    """
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return the precise name of the chunking strategy."""
        pass
        
    @abstractmethod
    def split(self, document: DocumentResponse) -> List[str]:
        """
        Takes a full DocumentResponse and returns a list of raw text strings.
        Must raise ChunkingException on failure.
        """
        pass
