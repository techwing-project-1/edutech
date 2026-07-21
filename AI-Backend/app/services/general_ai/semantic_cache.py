import time
import numpy as np
from typing import Optional
from app.core.logger import logger
from app.services.embeddings.manager import EmbeddingManager
from app.domain.schemas.embedding import EmbeddingRequest
from app.domain.schemas.llm import LLMResponse
from pydantic import BaseModel

class CacheEntry(BaseModel):
    query: str
    embedding: list[float]
    response: LLMResponse
    timestamp: float

class SemanticCacheService:
    """
    In-Memory Semantic Cache for LLM responses.
    Uses cosine similarity to determine if a cached response matches the incoming query.
    In a real production environment, this would be backed by Redis + Vector Search.
    """
    _cache: list[CacheEntry] = []
    _similarity_threshold: float = 0.95
    
    @classmethod
    def get(cls, query: str) -> Optional[LLMResponse]:
        """Search the semantic cache for a similar query."""
        if not cls._cache:
            return None
            
        try:
            embed_mgr = EmbeddingManager()
            req = EmbeddingRequest(texts=query)
            resp = embed_mgr.create_embeddings(req)
            query_emb = np.array(resp.embeddings[0])
            
            best_match = None
            highest_similarity = 0.0
            
            for entry in cls._cache:
                cached_emb = np.array(entry.embedding)
                # Compute cosine similarity
                cos_sim = np.dot(query_emb, cached_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(cached_emb))
                if cos_sim > highest_similarity:
                    highest_similarity = cos_sim
                    best_match = entry
                    
            if highest_similarity >= cls._similarity_threshold and best_match:
                logger.info(f"Semantic Cache Hit! Similarity: {highest_similarity:.4f}")
                # Update latency metrics to show cache hit speed
                cached_response = best_match.response.model_copy()
                cached_response.provider_used = "Semantic Cache"
                cached_response.fallback_used = False
                return cached_response
                
        except Exception as e:
            logger.warning(f"Semantic Cache get failed: {str(e)}")
            
        return None

    @classmethod
    def set(cls, query: str, response: LLMResponse):
        """Add a new query and response to the semantic cache."""
        try:
            embed_mgr = EmbeddingManager()
            req = EmbeddingRequest(texts=query)
            resp = embed_mgr.create_embeddings(req)
            query_emb = resp.embeddings[0]
            
            # Maintain a bounded cache size (e.g., last 1000 items)
            if len(cls._cache) > 1000:
                cls._cache.pop(0)
                
            entry = CacheEntry(
                query=query,
                embedding=query_emb,
                response=response,
                timestamp=time.time()
            )
            cls._cache.append(entry)
            logger.debug("Stored response in Semantic Cache.")
        except Exception as e:
            logger.warning(f"Semantic Cache set failed: {str(e)}")
