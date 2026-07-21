from typing import List
from app.domain.schemas.retriever import RetrievedChunk
from app.core.rag_config import rag_config
import re

class ContextBuilder:
    """
    Formats the raw Vector Store chunks into a cohesive string context for the LLM Prompt.
    Includes text deduplication to optimize context windows and prevent repetitive generation.
    """
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Removes extra whitespace, lowers case for comparison."""
        return re.sub(r'\s+', ' ', text).strip().lower()

    @staticmethod
    def build_context_string(chunks: List[RetrievedChunk]) -> str:
        """
        Iterates over the validated chunks, maintains order, deduplicates overlapping/repeated text,
        and joins them using the configured separator.
        """
        if not chunks:
            return "No context found."
            
        # 1. Sort by relevance (score DESC)
        sorted_chunks = sorted(chunks, key=lambda c: c.score, reverse=True)
        
        # 2. Build structured citations with Deduplication
        context_parts = []
        seen_texts = set()
        
        for chunk in sorted_chunks:
            # Skip if we've seen this exact chunk text already (prevents duplicate document indexing issues)
            normalized_chunk = ContextBuilder._normalize_text(chunk.text)
            if normalized_chunk in seen_texts:
                continue
            
            # Simple substring deduplication: if this chunk is entirely contained in an already added chunk
            is_subset = False
            for seen in seen_texts:
                if normalized_chunk in seen:
                    is_subset = True
                    break
            
            if is_subset:
                continue
                
            seen_texts.add(normalized_chunk)
                
            file_name = getattr(chunk.metadata, 'document_name', "Unknown Document") if chunk.metadata else "Unknown Document"
            page_num = getattr(chunk.metadata, 'page_number', "N/A") if chunk.metadata else "N/A"
            chunk_id = getattr(chunk.metadata, 'chunk_id', chunk.id) if chunk.metadata else chunk.id
            
            # Extract first line as a proxy for Topic
            text_lines = chunk.text.strip().split('\n')
            topic_proxy = text_lines[0].strip() if text_lines else "Unknown Topic"
            
            # Formatted citation explicitly requested
            formatted_chunk = f"Document: {file_name}\nPage {page_num}\nTopic: {topic_proxy}\nText:\n{chunk.text.strip()}"
            context_parts.append(formatted_chunk)
            
        return rag_config.context_chunk_separator.join(context_parts)
