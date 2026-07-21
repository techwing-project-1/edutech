import threading
from typing import List
from sentence_transformers import SentenceTransformer
from app.core.embedding_config import embedding_config
from app.core.exceptions import EmbeddingException
from app.core.logger import logger

class EmbeddingService:
    """
    Singleton service that loads the HuggingFace model once during startup
    and reuses it for all subsequent requests. 
    Crucial for memory efficiency and performance.
    """
    _instance = None
    _lock = threading.Lock()
    _model = None

    def __new__(cls):
        # Thread-safe Singleton instantiation
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingService, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Loads the sentence-transformer model into memory."""
        try:
            logger.info(f"Initializing Embedding Model: {embedding_config.model_name}")
            # Loading model. In production, this runs once during application boot.
            self._model = SentenceTransformer(embedding_config.model_name)
            logger.info(f"Embedding Model '{embedding_config.model_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise EmbeddingException(f"Failed to initialize embedding model: {str(e)}")

    def embed_text(self, text: str) -> List[float]:
        """Generates embedding for a single string."""
        try:
            # Generate embedding and convert numpy array to standard python list
            # We explicitly normalize embeddings so L2 distance mathematically maps strictly to Cosine Distance
            embedding = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding single text: {str(e)}")
            raise EmbeddingException(f"Failed to embed single text: {str(e)}")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of strings efficiently."""
        try:
            embeddings = self._model.encode(
                texts, 
                batch_size=embedding_config.batch_size, 
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding batch texts: {str(e)}")
            raise EmbeddingException(f"Failed to embed batch texts: {str(e)}")
            
    def get_dimension(self) -> int:
        """Returns the output dimension size (e.g. 384 for MiniLM)."""
        if self._model:
            return self._model.get_sentence_embedding_dimension()
        return 0
