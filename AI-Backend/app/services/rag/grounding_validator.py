import re
from typing import List
from app.domain.schemas.retriever import RetrievedChunk
from app.core.logger import logger
from app.core.exceptions import HallucinationException

class GroundingValidator:
    """
    Validates that LLM generated text is grounded in the retrieved chunks.
    """
    
    @staticmethod
    def _extract_sentences(text: str) -> List[str]:
        """Simple regex based sentence extraction."""
        # Split on ., !, ? followed by whitespace or end of string.
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip().lower() for s in sentences if len(s.strip()) > 10]
        
    @staticmethod
    def _compute_overlap(sentence: str, reference_text: str) -> float:
        """Computes basic word overlap percentage (Jaccard-like index of words)."""
        sent_words = set(re.findall(r'\w+', sentence))
        if not sent_words:
            return 1.0 # Ignore empty/symbol only sentences
            
        ref_words = set(re.findall(r'\w+', reference_text.lower()))
        
        intersection = sent_words.intersection(ref_words)
        return len(intersection) / len(sent_words)

    @staticmethod
    def validate_grounding(generated_text: str, retrieved_chunks: List[RetrievedChunk], threshold: float = 0.15) -> bool:
        """
        Validates if the generated text is sufficiently grounded in the retrieved chunks.
        Requires at least `threshold` % word overlap across all sentences on average.
        For true RAG, we don't want completely disjoint generated text.
        """
        if not retrieved_chunks:
            logger.warning("Grounding validation skipped: No chunks provided.")
            return False
            
        combined_context = " ".join([c.text for c in retrieved_chunks])
        sentences = GroundingValidator._extract_sentences(generated_text)
        
        if not sentences:
            return True # Output was not sentences (e.g., JSON structure alone)
            
        total_overlap = 0.0
        grounded_sentences = 0
        
        for sentence in sentences:
            overlap = GroundingValidator._compute_overlap(sentence, combined_context)
            total_overlap += overlap
            if overlap >= 0.2: # If 20% of the words are in context, it's roughly grounded
                grounded_sentences += 1
                
        avg_overlap = total_overlap / len(sentences)
        logger.info(f"Grounding Score: {avg_overlap:.2f} avg word overlap, {grounded_sentences}/{len(sentences)} sentences grounded.")
        
        if avg_overlap < threshold:
            logger.error(f"Grounding validation failed! Score: {avg_overlap:.2f} < {threshold}")
            raise HallucinationException("Generated content failed grounding validation against retrieved syllabus context.")
            
        return True
