from app.domain.interfaces.document_loader import DocumentLoaderInterface
from app.domain.schemas.document import DocumentResponse, DocumentMetadata
from app.core.logger import logger
from app.utils.file_utils import get_file_size
import os

from typing import List

class TXTLoader(DocumentLoaderInterface):
    """
    Handles basic text file processing.
    """
    
    async def load(self, file_path: str) -> List[DocumentResponse]:
        logger.info(f"Loading TXT document: {file_path}")
        
        # Future Logic: Read raw string
        
        metadata = DocumentMetadata(
            file_name=os.path.basename(file_path),
            file_size_bytes=get_file_size(file_path),
            file_extension=".txt"
        )
        
        return [DocumentResponse(
            content="[SIMULATED] TXT text content extracted successfully.",
            metadata=metadata
        )]

    def supports_ocr(self) -> bool:
        return False
