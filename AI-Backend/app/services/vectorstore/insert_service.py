from typing import List
from app.infrastructure.vectorstore.factory import VectorStoreFactory
from app.domain.schemas.vectorstore import VectorRecord
from app.services.vectorstore.validator import VectorValidator
from app.core.vectorstore_config import vs_config

class VectorInsertService:
    """
    Service responsible for safely routing Single and Batch records into the Vector Store.
    """
    
    @staticmethod
    def insert_single(record: VectorRecord, collection_name: str = vs_config.default_collection) -> None:
        """Wraps a single record into a batch operation for unified architecture flow."""
        VectorInsertService.insert_batch([record], collection_name)
        
    @staticmethod
    def insert_batch(records: List[VectorRecord], collection_name: str = vs_config.default_collection) -> None:
        """Validates and executes batch upsert via the dynamic Provider."""
        VectorValidator.validate_records(records)
        
        provider = VectorStoreFactory.get_provider()
        provider.insert(collection_name, records)
