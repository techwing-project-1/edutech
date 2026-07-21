import httpx
from google.genai import errors as genai_errors
from app.core.exceptions import (
    ProviderUnavailable,
    TimeoutError,
    RateLimitExceeded,
    LLMProviderException,
    ProviderResponseParsingError,
    ProviderAuthenticationError,
    ProviderAuthorizationError,
    ProviderQuotaExceeded
)
from app.core.logger import logger

class ErrorMapper:
    """
    Standardizes exceptions across different providers into DomainExceptions.
    """
    
    @staticmethod
    def map_openrouter_error(e: Exception) -> Exception:
        """Maps HTTP and OpenRouter errors."""
        if isinstance(e, httpx.TimeoutException):
            return TimeoutError(f"OpenRouter timeout: {str(e)}")
        
        if isinstance(e, httpx.HTTPStatusError):
            status = e.response.status_code
            text = e.response.text
            logger.error(f"OpenRouter HTTP Error {status}: {text}")
            
            if status == 429:
                return RateLimitExceeded("OpenRouter rate limit exceeded.")
            elif status == 402:
                return ProviderQuotaExceeded("OpenRouter insufficient credits.")
            elif status == 401:
                return ProviderAuthenticationError("OpenRouter authentication failed (API key invalid or missing).")
            elif status == 403:
                return ProviderAuthorizationError("OpenRouter authorization failed (Model access denied).")
            elif status >= 500:
                return ProviderUnavailable(f"OpenRouter server error: {status}")
            else:
                return LLMProviderException(f"OpenRouter API error {status}: {text}")
                
        if isinstance(e, httpx.RequestError):
            return ProviderUnavailable(f"OpenRouter network/connection error: {str(e)}")
            
        if isinstance(e, (ValueError, KeyError, TypeError)):
            return ProviderResponseParsingError(f"OpenRouter JSON parse error: {str(e)}")
            
        return LLMProviderException(f"OpenRouter unexpected error: {str(e)}")
        
    @staticmethod
    def map_gemini_error(e: Exception) -> Exception:
        """Maps google-genai API errors."""
        if isinstance(e, genai_errors.APIError):
            logger.error(f"Gemini API Error {e.code}: {e.message}")
            if e.code == 429:
                return RateLimitExceeded(f"Gemini rate limit exceeded: {e.message}")
            elif e.code == 402:
                return ProviderQuotaExceeded(f"Gemini quota exhausted: {e.message}")
            elif e.code == 401:
                return ProviderAuthenticationError(f"Gemini authentication failed: {e.message}")
            elif e.code == 403:
                return ProviderAuthorizationError(f"Gemini authorization failed: {e.message}")
            elif e.code >= 500:
                return ProviderUnavailable(f"Gemini server error: {e.message}")
            else:
                return LLMProviderException(f"Gemini API error {e.code}: {e.message}")
                
        # Since we use asyncio.wait_for, TimeoutError will be caught by the manager natively.
        # But if SDK raises a timeout or request error:
        name = type(e).__name__
        if "timeout" in name.lower():
            return TimeoutError(f"Gemini timeout: {str(e)}")
            
        if isinstance(e, (ValueError, KeyError)):
            return ProviderResponseParsingError(f"Gemini malformed response: {str(e)}")
            
        return LLMProviderException(f"Gemini unexpected error: {str(e)}")
