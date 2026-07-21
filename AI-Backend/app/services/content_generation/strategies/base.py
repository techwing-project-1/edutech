from abc import ABC, abstractmethod
from app.domain.schemas.content_generation import ContentGenerationRequest
from app.domain.schemas.llm import LLMRequest

class BaseContentGenerator(ABC):
    """
    Base strategy class for all content generators.
    Specific modes (Summary, Quiz, etc.) will implement this interface.
    """
    
    @abstractmethod
    def build_prompt(self, request: ContentGenerationRequest, context: str) -> LLMRequest:
        """
        Builds the LLMRequest specific to the generation mode.
        """
        pass

    def _get_strict_anti_hallucination_rules(self) -> str:
        """
        Standard anti-hallucination rules applied across all RAG generators.
        """
        return """
STRICT ANTI-HALLUCINATION RULES:
1. You MUST ONLY use the provided context to answer. 
2. DO NOT invent, guess, hallucinate, or use general model knowledge.
3. If the context does not contain enough information to generate the requested content ABOUT THE EXACT REQUESTED TOPIC, you MUST stop and respond EXACTLY with: "No relevant information was found in the uploaded document related to your question."
4. DO NOT generate ANY introductory or concluding sentences. (e.g., DO NOT say "Based on the provided document...", "Here is the summary...", "I hope this helps.", etc.). Generate the final answer directly.
5. EVERY generated answer or claim MUST include a citation exactly matching the provided source metadata.
Format citations exactly as:
Source:
[file_name]
Page [page_num]
Chunk [chunk_id]
"""
