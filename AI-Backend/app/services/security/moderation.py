import re
from typing import List, Tuple
from app.core.exceptions import PromptInjectionDetected
from app.core.logger import logger

class ModerationService:
    """
    Security layer for analyzing inputs and outputs.
    Implements basic prompt injection heuristics and content filtering.
    """
    
    # Simple heuristics for demonstration.
    # In production, replace with LLM-based moderation (e.g. OpenAI Moderation API)
    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous\s+)?instructions", re.IGNORECASE),
        re.compile(r"disregard\s+(all\s+)?(previous\s+)?instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt", re.IGNORECASE),
        re.compile(r"you\s+are\s+now", re.IGNORECASE),
        re.compile(r"DAN", re.IGNORECASE), # Do Anything Now
        re.compile(r"forget\s+everything", re.IGNORECASE),
        re.compile(r"print\s+your\s+initial\s+prompt", re.IGNORECASE),
        re.compile(r"what\s+are\s+your\s+rules", re.IGNORECASE),
        re.compile(r"reveal\s+your\s+instructions", re.IGNORECASE)
    ]

    @classmethod
    def check_for_injection(cls, query: str) -> None:
        """
        Validates user input against known jailbreak patterns.
        Raises PromptInjectionDetected if malicious intent is suspected.
        """
        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(query):
                logger.warning(f"Prompt injection detected for query: {query[:50]}...")
                raise PromptInjectionDetected("Security Alert: Prompt injection or jailbreak attempt detected.")
        
        # Add more robust validation here if needed
        return None

    @classmethod
    def filter_output(cls, output: str) -> str:
        """
        Filters output for sensitive information or toxic content.
        Currently a no-op, extensible for future use.
        """
        return output
