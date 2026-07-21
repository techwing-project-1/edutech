from typing import List, Optional
from app.domain.schemas.vectorstore import VectorRecord, VectorSearchResponse, CollectionStats
from app.services.vectorstore.insert_service import VectorInsertService
from app.services.vectorstore.search_service import VectorSearchService
from app.services.vectorstore.delete_service import VectorDeleteService
from app.services.vectorstore.collection_service import CollectionService
from app.core.vectorstore_config import vs_config

class VectorStoreManager:
    """
    High-level Orchestrator / Facade for the Vector Database.
    Exposes unified access to Insert, Search, Delete, and Collection Services.
    """
    
    @staticmethod
    def insert(records: List[VectorRecord], collection_name: str = vs_config.default_collection) -> None:
        VectorInsertService.insert_batch(records, collection_name)
        
    @staticmethod
    def search(query_embedding: List[float], top_k: int = vs_config.top_k_default, collection_name: str = vs_config.default_collection, metadata_filter: Optional[dict] = None, explain_mode: bool = False) -> VectorSearchResponse:
        return VectorSearchService.search(query_embedding, top_k, collection_name, metadata_filter, explain_mode)
        
    @staticmethod
    def delete_document(document_id: str, collection_name: str = vs_config.default_collection) -> None:
        VectorDeleteService.delete_by_document(document_id, collection_name)
        
    @staticmethod
    def delete_collection(collection_name: str = vs_config.default_collection) -> None:
        VectorDeleteService.delete_entire_collection(collection_name)
        
    @staticmethod
    def get_stats(collection_name: str = vs_config.default_collection) -> CollectionStats:
        return CollectionService.get_stats(collection_name)
