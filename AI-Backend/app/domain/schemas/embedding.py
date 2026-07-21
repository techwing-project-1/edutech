from pydantic import BaseModel, Field
from typing import List, Union

class EmbeddingRequest(BaseModel):
    """
    Request model for the Embedding Layer.
    Supports single text (str) or batch processing (List[str]).
    """
    texts: Union[str, List[str]] = Field(..., description="A single text string or a list of text strings to embed.")

class EmbeddingResponse(BaseModel):
    """
    Standardized Embedding Response.
    Designed to interface smoothly with Vector Databases (ChromaDB / OpenSearch).
    """
    embeddings: List[List[float]] = Field(..., description="A list of numerical vectors representing the text.")
    model_used: str = Field(..., description="The exact model name used to generate the embeddings.")
    dimension: int = Field(..., description="The vector dimensionality (e.g., 384 for MiniLM-L6-v2).")
