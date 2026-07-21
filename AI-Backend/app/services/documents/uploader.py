import os
from fastapi import UploadFile
from app.core.document_config import doc_config
from app.core.logger import logger
from app.utils.file_utils import generate_secure_filename

class UploadManager:
    """
    Safely streams FastAPI UploadFiles to a temporary local disk location.
    Essential for processing large files without exhausting RAM.
    """
    
    @staticmethod
    async def save_upload(file: UploadFile) -> str:
        # Ensure temp directory exists
        os.makedirs(doc_config.upload_temp_dir, exist_ok=True)
        
        # Generate secure filename to prevent path traversal
        secure_name = generate_secure_filename(file.filename)
        save_path = os.path.join(doc_config.upload_temp_dir, secure_name)
        
        logger.info(f"Saving uploaded document to temporary path: {save_path}")
        
        try:
            # Save file in chunks to optimize memory
            with open(save_path, "wb") as buffer:
                while content := await file.read(1024 * 1024):  # 1MB chunks
                    buffer.write(content)
        except Exception as e:
            logger.error(f"Upload Manager failed to save file: {str(e)}")
            # Cleanup partially saved file if exception occurs
            if os.path.exists(save_path):
                os.remove(save_path)
            raise
            
        return save_path
