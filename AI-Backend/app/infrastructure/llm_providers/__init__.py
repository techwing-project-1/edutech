# Init for llm_providers
from app.infrastructure.llm_providers.factory import LLMProviderType
from app.infrastructure.llm_providers.registry import ProviderRegistry
from app.infrastructure.llm_providers.gemini import GeminiProvider
from app.infrastructure.llm_providers.openrouter import OpenRouterProvider
from app.infrastructure.llm_providers.claude import ClaudeProvider
from app.infrastructure.llm_providers.deepseek import DeepSeekProvider
from app.infrastructure.llm_providers.openrouter_derived import (
    LlamaProvider, MistralProvider, QwenProvider, GemmaProvider
)

# Auto-register providers when the package is imported
ProviderRegistry.register(LLMProviderType.GEMINI, GeminiProvider)
ProviderRegistry.register(LLMProviderType.OPENROUTER, OpenRouterProvider)
ProviderRegistry.register(LLMProviderType.ANTHROPIC, ClaudeProvider)
ProviderRegistry.register(LLMProviderType.DEEPSEEK, DeepSeekProvider)
ProviderRegistry.register(LLMProviderType.LLAMA, LlamaProvider)
ProviderRegistry.register(LLMProviderType.MISTRAL, MistralProvider)
ProviderRegistry.register(LLMProviderType.QWEN, QwenProvider)
ProviderRegistry.register(LLMProviderType.GEMMA, GemmaProvider)

