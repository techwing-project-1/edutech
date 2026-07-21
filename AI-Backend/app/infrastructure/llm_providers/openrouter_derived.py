from app.infrastructure.llm_providers.openrouter import OpenRouterProvider

class LlamaProvider(OpenRouterProvider):
    """Llama Provider Adapter (Tunneled via OpenRouter for ease of access to Llama 3)"""
    @property
    def provider_name(self) -> str:
        return "Llama"
        
class QwenProvider(OpenRouterProvider):
    """Qwen Provider Adapter (Tunneled via OpenRouter)"""
    @property
    def provider_name(self) -> str:
        return "Qwen"
        
class GemmaProvider(OpenRouterProvider):
    """Gemma Provider Adapter (Tunneled via OpenRouter)"""
    @property
    def provider_name(self) -> str:
        return "Gemma"
        
class MistralProvider(OpenRouterProvider):
    """Mistral Provider Adapter (Tunneled via OpenRouter)"""
    @property
    def provider_name(self) -> str:
        return "Mistral"
