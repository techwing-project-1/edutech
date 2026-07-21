from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.schemas.vectorstore import VectorRecord, SearchResult, CollectionStats

class VectorStoreInterface(ABC):
    """
    Abstract interface enforcing the Provider Pattern for all Vector Databases.
    This guarantees that the future migration to Amazon OpenSearch requires ZERO changes to the business logic.
    """
    
    @abstractmethod
    def create_collection(self, collection_name: str) -> None:
        """Initialize a new collection/index."""
        pass
    
    @abstractmethod
    def insert(self, collection_name: str, records: List[VectorRecord]) -> None:
        """Insert or Upsert single or batch records."""
        pass
    
    @abstractmethod
    def search(self, collection_name: str, query_embedding: List[float], top_k: int, metadata_filter: Optional[dict] = None, explain_mode: bool = False) -> List[SearchResult]:
        """Perform a K-Nearest Neighbors (KNN) / Cosine Similarity Search."""
        pass
    
    @abstractmethod
    def delete_by_document_id(self, collection_name: str, document_id: str) -> None:
        """Remove all chunks associated with a specific document."""
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> None:
        """Destroy the entire collection and all vectors within."""
        pass
    
    @abstractmethod
    def get_collection_stats(self, collection_name: str) -> CollectionStats:
        """Retrieve total vector counts and metadata about the collection."""
        pass
