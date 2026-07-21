from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv

# Explicitly load .env into os.environ so all direct os.getenv() calls succeed
load_dotenv()

class Settings(BaseSettings):
    """
    Centralized configuration management for the AI Backend.
    Uses Pydantic BaseSettings to load environment variables.
    """
    PROJECT_NAME: str = "CurriculaMind AI Backend"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = ""

    # Future Database Integrations
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ai_backend.db"
    REDIS_URL: Optional[str] = None
    
    VECTOR_DB_HOST: Optional[str] = None
    VECTOR_DB_API_KEY: Optional[str] = None

    # AI Provider API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # LLM Provider Configuration
    PRIMARY_PROVIDER: str = "gemini"
    SECONDARY_PROVIDER: str = "openrouter"
    PROVIDER_ROUTING_ORDER: str = "gemini,openrouter"
    
    # Timeouts
    LLM_TIMEOUT: float = 15.0
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048
    MAX_CONTEXT_TOKENS: int = 128000
    AUTO_SUMMARIZE_THRESHOLD: int = 4000
    # Feature Flags
    ENABLE_AGENT_ROUTING: bool = True
    ENABLE_FALLBACK_PROVIDERS: bool = True
    ENABLE_METRICS: bool = True
    ENABLE_RAG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

# Instantiate settings to be imported across the app
settings = Settings()

# Post-instantiation validation to crash at startup if critical config is missing
if settings.ENVIRONMENT.lower() == "production":
    if not settings.GEMINI_API_KEY:
        from app.core.exceptions import InvalidConfigurationError
        raise InvalidConfigurationError("GEMINI_API_KEY must be set in production.")
    if not settings.VECTOR_DB_HOST:
        from app.core.exceptions import InvalidConfigurationError
        raise InvalidConfigurationError("VECTOR_DB_HOST must be set in production.")
