from app.infrastructure.vectorstore.factory import VectorStoreFactory
from app.core.vectorstore_config import vs_config

class VectorDeleteService:
    """
    Service responsible for surgical or complete deletion of data within the Vector Store.
    """
    
    @staticmethod
    def delete_by_document(document_id: str, collection_name: str = vs_config.default_collection) -> None:
        """Removes all embedded chunks that share a specific document_id."""
        provider = VectorStoreFactory.get_provider()
        provider.delete_by_document_id(collection_name, document_id)
        
    @staticmethod
    def delete_entire_collection(collection_name: str = vs_config.default_collection) -> None:
        """Permanently destroys a collection and all data within it."""
        provider = VectorStoreFactory.get_provider()
        provider.delete_collection(collection_name)
