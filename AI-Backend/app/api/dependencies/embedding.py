from app.services.embeddings.manager import EmbeddingManager

def get_embedding_manager() -> EmbeddingManager:
    """
    FastAPI dependency injection for EmbeddingManager.
    Ensures that the manager (and underlying singleton service) is easily available to routers.
    """
    return EmbeddingManager()
