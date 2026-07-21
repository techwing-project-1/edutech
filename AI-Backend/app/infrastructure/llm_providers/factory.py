from enum import Enum
from app.domain.interfaces.llm_provider import LLMProviderInterface
from app.core.exceptions import DomainException

class LLMProviderType(str, Enum):
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    GROQ = "groq"
    LLAMA = "llama"
    QWEN = "qwen"
    GEMMA = "gemma"

class LLMProviderFactory:
    """
    Factory pattern to dynamically instantiate LLM Providers.
    Delegates class resolution to the ProviderRegistry to decouple implementations.
    """
    
    @staticmethod
    def get_provider(provider_type: LLMProviderType) -> LLMProviderInterface:
        from app.infrastructure.llm_providers.registry import ProviderRegistry
        try:
            provider_class = ProviderRegistry.get_provider_class(provider_type)
            return provider_class()
        except DomainException:
            # Fallback to a dummy provider or log and raise
            raise DomainException(f"Provider {provider_type} is not properly registered or implemented.")
