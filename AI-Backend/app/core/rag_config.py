from pydantic import BaseModel

class RAGConfiguration(BaseModel):
    """
    Configuration settings specifically for the RAG orchestration layer.
    """
    max_context_tokens: int = 4000
    context_chunk_separator: str = "\n\n--- [Document Separator] ---\n\n"

rag_config = RAGConfiguration()
