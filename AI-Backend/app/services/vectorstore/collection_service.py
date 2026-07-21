from app.infrastructure.vectorstore.factory import VectorStoreFactory
from app.domain.schemas.vectorstore import CollectionStats
from app.core.vectorstore_config import vs_config

class CollectionService:
    """
    Service responsible for database-level lifecycle operations (create, stats).
    """
    
    @staticmethod
    def create(collection_name: str = vs_config.default_collection) -> None:
        provider = VectorStoreFactory.get_provider()
        provider.create_collection(collection_name)
        
    @staticmethod
    def get_stats(collection_name: str = vs_config.default_collection) -> CollectionStats:
        provider = VectorStoreFactory.get_provider()
        return provider.get_collection_stats(collection_name)
