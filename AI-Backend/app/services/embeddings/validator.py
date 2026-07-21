from typing import Union, List
from app.core.exceptions import EmbeddingException

class EmbeddingValidator:
    """
    Validates inputs before sending them to the expensive embedding model.
    Prevents corrupt or empty data from crashing the HuggingFace pipeline.
    """
    
    @staticmethod
    def validate_input(texts: Union[str, List[str]]) -> None:
        """Ensures that the input string or list of strings is not empty."""
        if not texts:
            raise EmbeddingException("Embedding Validation Failed: Input text cannot be empty.")
            
        if isinstance(texts, list):
            if len(texts) == 0:
                raise EmbeddingException("Embedding Validation Failed: Batch list cannot be empty.")
            for idx, text in enumerate(texts):
                if not isinstance(text, str) or not text.strip():
                    raise EmbeddingException(f"Embedding Validation Failed: Invalid or empty text at index {idx}.")
        else:
            if not isinstance(texts, str) or not texts.strip():
                raise EmbeddingException("Embedding Validation Failed: Invalid or empty text string.")
