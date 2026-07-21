import functools
from app.services.embeddings.service import EmbeddingService
from app.services.embeddings.validator import EmbeddingValidator
from app.domain.schemas.embedding import EmbeddingRequest, EmbeddingResponse
from app.core.embedding_config import embedding_config
from app.core.logger import logger

class EmbeddingManager:
    """
    High-level Orchestrator for the Embedding Layer.
    Exposed to the API/Application layer. Coordinates Validation and the Singleton Service.
    """
    
    def __init__(self):
        # Service is a Singleton, so instantiation here simply retrieves the existing model in memory
        self.service = EmbeddingService()

    @functools.lru_cache(maxsize=128)
    def _create_embeddings_cached(self, text: str) -> EmbeddingResponse:
        """Cached path for single text queries to improve RAG latency."""
        embeddings = [self.service.embed_text(text)]
        dimension = self.service.get_dimension()
        return EmbeddingResponse(
            embeddings=embeddings,
            model_used=embedding_config.model_name,
            dimension=dimension
        )

    def create_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Processes an EmbeddingRequest and returns standardized numerical vectors.
        Automatically handles routing for single text vs batch texts.
        """
        if isinstance(request.texts, str):
            # Use cached path for identical questions
            return self._create_embeddings_cached(request.texts)
            
        return self._create_embeddings_batch(request)
        
    def _create_embeddings_batch(self, request: EmbeddingRequest) -> EmbeddingResponse:
        logger.debug("Starting embedding generation process.")
        
        # 1. Validate Input
        EmbeddingValidator.validate_input(request.texts)
        
        # 2. Embed
        if isinstance(request.texts, str):
            logger.debug("Processing single text embedding.")
            embeddings = [self.service.embed_text(request.texts)]
        else:
            logger.debug(f"Processing batch embedding. Count: {len(request.texts)}")
            embeddings = self.service.embed_batch(request.texts)
            
        # 3. Formulate Response
        dimension = self.service.get_dimension()
        logger.info(f"Successfully generated {len(embeddings)} embeddings of dimension {dimension}.")
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model_used=embedding_config.model_name,
            dimension=dimension
        )
