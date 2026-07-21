from typing import Any
from app.domain.schemas.llm import LLMResponse
from app.core.exceptions import ProviderResponseParsingError

def extract_text(response: Any) -> str:
    """
    Safely extracts the generated text from various LLM response formats.
    Supports:
    - Internal LLMResponse model
    - Raw dict responses (OpenRouter / JSON payloads)
    - Raw string responses (Streaming chunks)
    - Gemini SDK responses (with .text attribute)
    
    Raises ProviderResponseParsingError if the object cannot be parsed.
    """
    if response is None:
        raise ProviderResponseParsingError("LLM response is None.")
        
    if isinstance(response, str):
        return response
        
    if isinstance(response, LLMResponse):
        return response.answer
        
    if isinstance(response, dict):
        # OpenRouter standard format
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return str(choice["message"]["content"])
                
        # Common flat formats
        for key in ["text", "content", "answer", "output", "message"]:
            if key in response and response[key] is not None:
                return str(response[key])
                
    # Check for Gemini or generic objects with .text
    if hasattr(response, "text") and getattr(response, "text") is not None:
        return str(getattr(response, "text"))
        
    # Check for content attribute (e.g. Claude)
    if hasattr(response, "content") and getattr(response, "content") is not None:
        # Some SDKs return list for content
        content = getattr(response, "content")
        if isinstance(content, list) and len(content) > 0 and hasattr(content[0], "text"):
            return str(getattr(content[0], "text"))
        if isinstance(content, str):
            return content
            
    # Check for answer attribute
    if hasattr(response, "answer") and getattr(response, "answer") is not None:
        return str(getattr(response, "answer"))
        
    raise ProviderResponseParsingError(f"Failed to extract text from response type: {type(response)}")
