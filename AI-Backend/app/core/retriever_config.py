from pydantic_settings import BaseSettings, SettingsConfigDict

class RetrieverConfiguration(BaseSettings):
    """
    Configuration for the RAG Retriever Layer.
    """
    default_top_k: int = 5
    retrieval_threshold: float = 0.75
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

retriever_config = RetrieverConfiguration()
