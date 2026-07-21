from pydantic import BaseModel, Field, field_validator
from app.core.config import settings
from app.core.exceptions import LLMProviderException

class ProviderConfiguration(BaseModel):
    """
    Dedicated Provider Configuration layer.
    Extracts and validates environment variables specific to LLM Providers.
    Ensures fail-fast behavior if critical secrets are missing.
    """
    gemini_api_key: str = Field(default_factory=lambda: settings.GEMINI_API_KEY)
    openrouter_api_key: str = Field(default_factory=lambda: settings.OPENROUTER_API_KEY)
    timeout: int = Field(default_factory=lambda: settings.LLM_TIMEOUT)
    max_retries: int = Field(default_factory=lambda: settings.LLM_MAX_RETRIES)
    
    @field_validator("gemini_api_key", "openrouter_api_key")
    def validate_keys(cls, v, info):
        """Provider Validation: Ensure keys are not empty strings."""
        if not v or v.strip() == "":
            raise LLMProviderException(f"Configuration Validation Error: Missing API Key for {info.field_name}")
        return v

# Instantiate globally for the provider managers to use securely
provider_config = ProviderConfiguration()
