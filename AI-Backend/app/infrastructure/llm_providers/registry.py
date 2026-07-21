from typing import Dict, Type
from app.domain.interfaces.llm_provider import LLMProviderInterface
from app.infrastructure.llm_providers.factory import LLMProviderType
from app.core.exceptions import DomainException

class ProviderRegistry:
    """
    Centralized dynamic registry for LLM Providers.
    This fulfills the requirement of 'Provider Registry' and enables easy addition 
    of future providers without modifying the Factory directly.
    """
    _providers: Dict[LLMProviderType, Type[LLMProviderInterface]] = {}

    @classmethod
    def register(cls, provider_type: LLMProviderType, provider_class: Type[LLMProviderInterface]):
        """Register a provider class against an enum type."""
        cls._providers[provider_type] = provider_class

    @classmethod
    def get_provider_class(cls, provider_type: LLMProviderType) -> Type[LLMProviderInterface]:
        """Retrieve the registered provider class."""
        if provider_type not in cls._providers:
            raise DomainException(f"Critical: Provider '{provider_type}' is not registered in the ProviderRegistry.")
        return cls._providers[provider_type]
