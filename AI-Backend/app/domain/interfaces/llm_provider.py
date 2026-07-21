from abc import ABC, abstractmethod
from app.domain.schemas.llm import LLMRequest, LLMResponse

class LLMProviderInterface(ABC):
    """
    Abstract Base Class representing an LLM Provider.
    Enforces the Provider Pattern and Dependency Injection.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the precise name of the provider."""
        pass
        
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text based on the standardized request.
        Must raise LLMProviderException on failure.
        """
        pass
        
    @abstractmethod
    async def generate_stream(self, request: LLMRequest):
        """
        Stream text generation based on the standardized request.
        Yields chunks of text.
        """
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Ping the provider to verify connectivity, authentication, and availability.
        """
        pass

    @property
    def supports_stream(self) -> bool:
        return True
        
    @property
    def supports_images(self) -> bool:
        return False
        
    @property
    def supports_tools(self) -> bool:
        return False
        
    @property
    def supports_json(self) -> bool:
        return False
