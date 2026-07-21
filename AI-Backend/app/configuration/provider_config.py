import os
from app.domain.schemas.configuration import ProviderConfigModel, VectorDBConfigModel

class ProviderConfig:
    @staticmethod
    def load() -> ProviderConfigModel:
        return ProviderConfigModel(
            primary_provider=os.getenv("PRIMARY_PROVIDER", "GEMINI"),
            fallback_enabled=os.getenv("FALLBACK_ENABLED", "True").lower() == "true",
            default_timeout=float(os.getenv("DEFAULT_TIMEOUT", "30.0")),
            retry_count=int(os.getenv("RETRY_COUNT", "3"))
        )

class VectorDBConfig:
    @staticmethod
    def load() -> VectorDBConfigModel:
        return VectorDBConfigModel(
            provider=os.getenv("VECTOR_DB", "OPENSEARCH"),
            host=os.getenv("VECTOR_DB_HOST", "localhost"),
            port=int(os.getenv("VECTOR_DB_PORT", "8000"))
        )

class AgentConfig:
    @staticmethod
    def load() -> dict:
        return {
            "max_concurrent_agents": int(os.getenv("MAX_CONCURRENT_AGENTS", "10")),
            "agent_timeout_seconds": int(os.getenv("AGENT_TIMEOUT", "60"))
        }

class ModelConfig:
    @staticmethod
    def load() -> dict:
        return {
            "gemini": os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest"),
            "openrouter": os.getenv("OPENROUTER_MODEL", "qwen/qwen3-8b:free"),
            "embeddings": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        }
