from typing import List
import math

class EmbeddingUtils:
    """
    Reusable utility functions for working with embeddings.
    """
    
    @staticmethod
    def normalize_l2(vector: List[float]) -> List[float]:
        """
        Normalizes a vector to length 1 (L2 normalization).
        Crucial for fast and accurate cosine similarity comparisons in Vector Databases.
        """
        norm = math.sqrt(sum(x * x for x in vector))
        if norm == 0:
            return vector
        return [x / norm for x in vector]
