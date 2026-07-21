from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError
from typing import Optional
import os

from app.infrastructure.opensearch.exceptions import ConfigurationError
from app.infrastructure.opensearch.logger import opensearch_logger

class OpenSearchSettings(BaseSettings):
    """Configuration for OpenSearch connection."""
    
    OPENSEARCH_ENDPOINT: str = Field(default="")
    OPENSEARCH_USERNAME: str = Field(default="")
    OPENSEARCH_PASSWORD: str = Field(default="")
    AWS_REGION: str = Field(default="ap-south-1")
    OPENSEARCH_INDEX: str = Field(default="curriculamindrag")
    
    # Connection configurations
    OPENSEARCH_TIMEOUT: int = Field(default=30)
    OPENSEARCH_MAX_RETRIES: int = Field(default=3)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )
    
def get_opensearch_settings() -> OpenSearchSettings:
    """
    Loads and validates OpenSearch settings.
    Raises ConfigurationError if essential fields are missing.
    """
    try:
        settings = OpenSearchSettings()
        
        # Check if we have the minimum required configuration to attempt a connection
        # Only raise if someone is actually trying to use OpenSearch (Phase 2),
        # but for Phase 1 we just validate if it's provided or missing.
        if not settings.OPENSEARCH_ENDPOINT:
            raise ConfigurationError("OPENSEARCH_ENDPOINT environment variable is missing or empty.")
            
        if not settings.OPENSEARCH_USERNAME or not settings.OPENSEARCH_PASSWORD:
            raise ConfigurationError("OpenSearch authentication credentials (USERNAME/PASSWORD) are missing.")
            
        return settings
    except ValidationError as e:
        opensearch_logger.error(f"OpenSearch configuration validation failed: {str(e)}")
        raise ConfigurationError(f"Invalid OpenSearch configuration: {str(e)}")

# Create a singleton instance accessible where needed
try:
    opensearch_settings = get_opensearch_settings()
except ConfigurationError as e:
    # We log it, but we don't crash the import phase. 
    # The actual startup hook will handle the graceful fallback for Phase 1.
    opensearch_logger.warning(f"OpenSearch is not fully configured: {str(e)}")
    opensearch_settings = None
