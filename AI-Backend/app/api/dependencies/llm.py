from fastapi import Depends
from app.services.llm.manager import LLMManager

def get_llm_manager() -> LLMManager:
    """
    Dependency Injection provider for the LLMManager.
    Allows FastAPI endpoints to easily inject the LLM Manager without manual instantiation.
    """
    return LLMManager()
