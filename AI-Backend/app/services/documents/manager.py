import os
from fastapi import UploadFile
from app.services.documents.uploader import UploadManager
from app.services.documents.validator import DocumentValidator
from app.infrastructure.document_parser.factory import DocumentLoaderFactory
from app.services.documents.cleaner import DocumentCleaner
from app.services.documents.metadata import DocumentMetadataExtractor
from app.domain.schemas.document import DocumentResponse
from app.core.logger import logger

from typing import List

class DocumentManager:
    """
    High-level orchestrator for the entire Document Processing pipeline.
    Coordinates Upload -> Validation -> Parsing -> Cleaning -> Metadata Enhancement.
    """
    
    @staticmethod
    async def process_upload(file: UploadFile) -> List[DocumentResponse]:
        logger.info(f"Starting pipeline for document: {file.filename}")
        
        file_path = ""
        try:
            # 1. Securely stream to disk
            file_path = await UploadManager.save_upload(file)
            
            # 2. Validate format and limits
            DocumentValidator.validate(file_path, getattr(file, "content_type", None))
            
            # 3. Route to specific loader (PDF/DOCX/TXT) via Factory
            loader = DocumentLoaderFactory.get_loader(file_path)
            doc_responses = await loader.load(file_path)
            
            # 4 & 5. Clean text and enhance metadata for each page
            for doc in doc_responses:
                doc.content = DocumentCleaner.clean(doc.content)
                doc.metadata = DocumentMetadataExtractor.enhance_metadata(doc.metadata)
            
            logger.info("Document pipeline completed. Pages are ready for Chunking.")
            return doc_responses
            
        finally:
            # 6. Guaranteed Cleanup of temporary files to prevent disk leak
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
