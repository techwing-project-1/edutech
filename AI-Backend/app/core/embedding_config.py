import os
from pydantic import BaseModel

class EmbeddingConfiguration(BaseModel):
    """
    Configuration for the Embedding Layer.
    Forces the use of a finalized HuggingFace model.
    """
    # The finalized embedding model for the project
    model_name: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Maximum number of texts to process in a single batch
    batch_size: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

embedding_config = EmbeddingConfiguration()
