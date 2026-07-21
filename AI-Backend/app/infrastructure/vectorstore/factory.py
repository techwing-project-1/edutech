from app.domain.interfaces.vector_store import VectorStoreInterface
# Removed ChromaDBProvider import
from app.infrastructure.vectorstore.opensearch_provider import OpenSearchProvider
from app.core.vectorstore_config import vs_config
from app.core.exceptions import VectorStoreException

class VectorStoreFactory:
    """
    Factory Pattern to abstract away the specific database implementation.
    Currently hardcoded to enforce OpenSearch as per Phase 2 migration.
    """
    
    @classmethod
    def get_provider(cls) -> VectorStoreInterface:
        provider = vs_config.provider.lower()
        if provider == "opensearch":
            return OpenSearchProvider()
        else:
            # Enforce OpenSearch gracefully even if config wasn't perfectly updated yet
            from app.core.logger import logger
            logger.warning(f"Vector Store Provider was set to '{provider}', but system strictly enforces 'opensearch'. Coercing provider.")
            return OpenSearchProvider()
