from app.domain.interfaces.document_loader import DocumentLoaderInterface
from app.domain.schemas.document import DocumentResponse, DocumentMetadata
from app.core.exceptions import DocumentProcessingException
from app.core.logger import logger
from app.utils.file_utils import get_file_size
import os
import docx
from typing import List

class DOCXLoader(DocumentLoaderInterface):
    """
    Handles DOCX (Microsoft Word) processing using python-docx.
    Simulates pagination by splitting text into logical pages based on character count.
    """
    
    def __init__(self, chars_per_page: int = 1500):
        self.chars_per_page = chars_per_page
        
    async def load(self, file_path: str) -> List[DocumentResponse]:
        logger.info(f"Loading DOCX document: {file_path}")
        
        responses = []
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    full_text.append(text)
            
            combined_text = "\n".join(full_text)
            
            # Simulate pagination
            page_num = 1
            file_name = os.path.basename(file_path)
            file_size = get_file_size(file_path)
            
            if not combined_text:
                return responses
                
            total_pages = max(1, (len(combined_text) + self.chars_per_page - 1) // self.chars_per_page)
            
            for i in range(0, len(combined_text), self.chars_per_page):
                page_text = combined_text[i:i + self.chars_per_page]
                
                metadata = DocumentMetadata(
                    file_name=file_name,
                    file_size_bytes=file_size,
                    file_extension=".docx",
                    page_count=total_pages,
                    page_number=page_num,
                    source_file_type="docx"
                )
                
                responses.append(DocumentResponse(content=page_text, metadata=metadata))
                page_num += 1
                
        except Exception as e:
            logger.error(f"python-docx Extraction Failed: {str(e)}")
            raise DocumentProcessingException(f"Failed to process DOCX: {str(e)}")
            
        return responses

    def supports_ocr(self) -> bool:
        return False
