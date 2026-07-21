from typing import List
from app.domain.schemas.vectorstore import VectorRecord
from app.core.exceptions import VectorStoreException

class VectorValidator:
    """
    Validates records prior to insertion to prevent corrupt or partial data
    from polluting the Vector Database index.
    """
    
    @staticmethod
    def validate_records(records: List[VectorRecord]) -> None:
        if not records:
            raise VectorStoreException("Insert Failed: Record list cannot be empty.")
            
        for idx, record in enumerate(records):
            if not record.id or not record.id.strip():
                raise VectorStoreException(f"Validation Error: Record at index {idx} has an empty ID.")
            
            if not record.embedding or len(record.embedding) == 0:
                raise VectorStoreException(f"Validation Error: Record '{record.id}' lacks a numerical embedding vector.")
            
            if not record.document_text or not record.document_text.strip():
                raise VectorStoreException(f"Validation Error: Record '{record.id}' lacks raw document text.")
