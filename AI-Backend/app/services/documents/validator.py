from app.core.document_config import doc_config
from app.core.exceptions import DocumentProcessingException
from app.utils.file_utils import get_file_extension, get_file_size
from app.core.logger import logger
import os

class DocumentValidator:
    """
    Validates uploaded documents to enforce enterprise security and memory limits.
    Prevents unsupported files and excessively large files from crashing the pipeline.
    """
    
    @staticmethod
    def validate(file_path: str, content_type: str = None) -> None:
        logger.debug(f"Validating document: {file_path}")
        
        # 1. Check if file exists
        if not os.path.exists(file_path):
            raise DocumentProcessingException("Document validation failed: File does not exist.", status_code=400)
            
        # 2. Check Extension and MIME type
        ext = get_file_extension(file_path)
        if ext not in doc_config.allowed_extensions:
            raise DocumentProcessingException(f"Unsupported extension '{ext}'. Allowed: {doc_config.allowed_extensions}", status_code=400)
            
        if content_type and hasattr(doc_config, 'allowed_mime_types'):
            if content_type not in doc_config.allowed_mime_types:
                raise DocumentProcessingException(f"Unsupported MIME type '{content_type}'.", status_code=400)
            
        # 3. Check Size
        size_bytes = get_file_size(file_path)
        max_bytes = doc_config.max_file_size_mb * 1024 * 1024
        
        if size_bytes > max_bytes:
            raise DocumentProcessingException(f"File size exceeds maximum allowed ({doc_config.max_file_size_mb} MB).", status_code=400)
        if size_bytes == 0:
            raise DocumentProcessingException("Document validation failed: File is empty.")
