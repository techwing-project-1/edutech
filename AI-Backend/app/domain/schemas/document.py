from pydantic import BaseModel, Field
from typing import Optional

class DocumentMetadata(BaseModel):
    """
    Structured metadata extracted from the document.
    Crucial for filtering in Vector Databases (ChromaDB / OpenSearch) later.
    """
    file_name: str
    file_size_bytes: int
    file_extension: str
    mime_type: Optional[str] = None
    page_count: Optional[int] = None
    page_number: Optional[int] = None
    source_file_type: Optional[str] = None
    author: Optional[str] = None
    
    # Future Flags for advanced pipeline routing
    is_scanned: bool = False
    requires_ocr: bool = False

class DocumentResponse(BaseModel):
    """
    Standardized extracted document representation.
    Designed specifically to map perfectly to LangChain's standard `Document` class
    when chunking and embeddings are implemented in the next phase.
    """
    content: str = Field(..., description="The raw, cleaned extracted text.")
    metadata: DocumentMetadata = Field(..., description="The associated metadata for the document.")
