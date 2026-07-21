from app.domain.interfaces.document_loader import DocumentLoaderInterface
from app.domain.schemas.document import DocumentResponse, DocumentMetadata
from app.core.exceptions import DocumentProcessingException
from app.core.logger import logger
from app.utils.file_utils import get_file_size
import os

from typing import List
import fitz

class PDFLoader(DocumentLoaderInterface):
    """
    Handles PDF Document Processing using PyMuPDF (fitz).
    Yields one DocumentResponse per page, enabling page_number tracking.
    """
    
    async def load(self, file_path: str) -> List[DocumentResponse]:
        logger.info(f"Loading PDF document with PyMuPDF: {file_path}")
        
        responses = []
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            file_size = get_file_size(file_path)
            file_name = os.path.basename(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text").strip()
                
                if not text:
                    continue # Skip empty pages
                    
                metadata = DocumentMetadata(
                    file_name=file_name,
                    file_size_bytes=file_size,
                    file_extension=".pdf",
                    page_count=len(doc),
                    page_number=page_num + 1,
                    source_file_type="pdf",
                    is_scanned=False,
                    requires_ocr=False
                )
                
                responses.append(DocumentResponse(content=text, metadata=metadata))
        except Exception as e:
            logger.error(f"PyMuPDF Extraction Failed: {str(e)}")
            raise DocumentProcessingException(f"Failed to process PDF: {str(e)}")
        finally:
            if 'doc' in locals() and doc:
                doc.close()
            
        return responses

    def supports_ocr(self) -> bool:
        return False
