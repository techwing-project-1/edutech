from pydantic import BaseModel
from typing import List

class DocumentConfiguration(BaseModel):
    """
    Configuration for Document Processing Layer.
    Controls limits, formats, and advanced extraction flags.
    """
    max_file_size_mb: int = 50
    allowed_extensions: List[str] = [".pdf", ".docx"]
    allowed_mime_types: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    upload_temp_dir: str = "./data/uploads"
    
    # Future OCR / Scanned PDF Support
    enable_ocr: bool = False

# Global configuration instance
doc_config = DocumentConfiguration()
