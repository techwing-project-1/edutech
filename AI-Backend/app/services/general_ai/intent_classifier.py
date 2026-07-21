import asyncio
import json
from app.services.llm.manager import LLMManager
from app.domain.schemas.llm import LLMRequest
from app.services.llm.parser import extract_text
from app.core.logger import logger
from app.infrastructure.llm_providers.factory import LLMProviderType

class QueryClassifier:
    """
    Lightweight intent classifier to personalize response formatting.
    Uses a fast/cheap LLM (e.g. Gemini Flash) to quickly determine the response type.
    """
    def __init__(self):
        self.llm_manager = LLMManager()

    async def classify(self, query: str) -> dict:
        """
        Fast, local heuristic for intent classification.
        Eliminates 2-3s of latency by avoiding the LLM round-trip.
        """
        q_lower = query.lower()
        response_type = "General"
        
        if any(word in q_lower for word in ["how to code", "python", "javascript", "error", "debug", "function"]):
            response_type = "Programming"
        elif any(word in q_lower for word in ["what is", "explain", "how does", "tutorial"]):
            response_type = "Educational"
        elif any(word in q_lower for word in ["calculate", "math", "equation", "solve"]):
            response_type = "Math"
            
        return {
            "response_type": response_type,
            "language": "en"
        }
