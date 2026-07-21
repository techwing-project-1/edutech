from abc import ABC, abstractmethod
from typing import List
from app.domain.schemas.document import DocumentResponse

class DocumentLoaderInterface(ABC):
    """
    Abstract Base Class for Document Loaders.
    Forces all formats (PDF, DOCX, TXT, PPTX) to conform to the identical parsing contract.
    """
    
    @abstractmethod
    async def load(self, file_path: str) -> List[DocumentResponse]:
        """
        Extract text and metadata from the document on disk.
        """
        pass
        
    @abstractmethod
    def supports_ocr(self) -> bool:
        """
        Returns whether this specific loader has OCR capabilities configured.
        """
        pass
