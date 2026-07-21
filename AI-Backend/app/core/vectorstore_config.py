import os
from pydantic import BaseModel

class VectorStoreConfiguration(BaseModel):
    """
    Configuration for the Vector Store Layer.
    Controls default collections, provider selection, and search defaults.
    """
    # Default collection/index name for storing vectors
    default_collection: str = os.getenv("OPENSEARCH_INDEX", "curriculamindrag")
    
    # Provider pattern selection (enforced to 'opensearch')
    provider: str = os.getenv("VECTOR_STORE_PROVIDER", "opensearch")
    
    # Default Top-K documents to return during a similarity search
    top_k_default: int = 5

vs_config = VectorStoreConfiguration()

