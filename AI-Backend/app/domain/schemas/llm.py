from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class LLMRequest(BaseModel):
    """
    Standardized request model for any LLM Provider.
    Ensures all providers receive the same data format.
    """
    prompt: str = Field(..., description="The input text/prompt for the LLM")
    system_prompt: Optional[str] = Field(None, description="System instructions if applicable")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: int = Field(1024, description="Maximum tokens to generate")
    provider_name: Optional[str] = Field(None, description="Specific provider to use, overrides primary provider")
    model_name: Optional[str] = Field(None, description="Specific model to use, defaults to provider's default")
    enforce_json_mode: bool = Field(False, description="Whether to enforce native JSON mode in provider API if supported")

class TokenUsage(BaseModel):
    prompt_tokens: int = Field(0, description="Tokens used for the prompt")
    completion_tokens: int = Field(0, description="Tokens used for the completion")
    total_tokens: int = Field(0, description="Total tokens used")

class LLMResponse(BaseModel):
    """
    Standardized response model from any LLM Provider.
    Normalizes responses across Gemini, OpenRouter, etc.
    """
    answer: str = Field(..., description="The generated response text")
    
    @field_validator("answer", mode="before")
    @classmethod
    def validate_answer_not_empty(cls, v: str) -> str:
        if v is None or not str(v).strip():
            raise ValueError("LLM response answer cannot be empty")
        return str(v)
        
    provider_used: str = Field(..., description="The name of the provider that generated the response")
    model_name: str = Field(..., description="The exact model version used")
    latency_ms: int = Field(..., description="Time taken to generate the response in milliseconds")
    usage: TokenUsage = Field(..., description="Token usage statistics")
    finish_reason: str = Field("stop", description="Why generation stopped")
    fallback_used: bool = Field(False, description="Whether a fallback provider was used")
    confidence: Optional[float] = Field(None, description="Confidence score if available")
    cost: Optional[float] = Field(0.0, description="Estimated cost of this request")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific metadata")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")
    session_id: Optional[str] = Field(None, description="Session ID from the request")
    response_id: Optional[str] = Field(None, description="Provider specific response ID")
