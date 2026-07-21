from typing import List, Optional
from app.infrastructure.vectorstore.factory import VectorStoreFactory
from app.domain.schemas.vectorstore import VectorSearchResponse
from app.core.vectorstore_config import vs_config
from app.core.logger import logger

class VectorSearchService:
    """
    Service responsible for retrieving Semantic / K-Nearest Neighbor matches from the Vector Store.
    """
    
    @staticmethod
    def search(query_embedding: List[float], top_k: int = vs_config.top_k_default, collection_name: str = vs_config.default_collection, metadata_filter: Optional[dict] = None, explain_mode: bool = False) -> VectorSearchResponse:
        logger.debug(f"Executing Vector Search in '{collection_name}' for Top {top_k} results. Filter: {metadata_filter}")
        
        provider = VectorStoreFactory.get_provider()
        results = provider.search(collection_name, query_embedding, top_k, metadata_filter, explain_mode=explain_mode)
        
        return VectorSearchResponse(results=results)
