from typing import List
from app.domain.schemas.retriever import RetrievedChunk
from app.core.rag_config import rag_config
from app.core.exceptions import RAGException

class ContextValidator:
    """
    Validates the context size to prevent exceeding LLM token limits.
    """
    
    @staticmethod
    def validate_context_size(chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """
        Ensures the total concatenated context does not exceed token limits.
        If it does, truncates the list by dropping the lowest scoring chunks (which are at the end).
        """
        valid_chunks = []
        current_length = 0
        for chunk in chunks:
            # Extremely rough approximation: 1 token ~= 4 chars
            approx_tokens = len(chunk.text) // 4
            
            if current_length + approx_tokens > rag_config.max_context_tokens:
                # If we exceed the limit, truncate the chunk to fit the remaining space instead of failing
                remaining_tokens = rag_config.max_context_tokens - current_length
                if remaining_tokens > 0:
                    allowed_chars = remaining_tokens * 4
                    # Truncate text and add indicator
                    chunk.text = chunk.text[:allowed_chars] + "...[TRUNCATED]"
                    valid_chunks.append(chunk)
                break
                
            valid_chunks.append(chunk)
            current_length += approx_tokens
            
        return valid_chunks
