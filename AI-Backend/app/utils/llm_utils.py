import re
from typing import Dict, Any

def count_words(text: str) -> int:
    """
    Reusable utility: Simple word counter.
    Useful for basic prompt length estimation before sending to providers.
    """
    if not text:
        return 0
    return len(re.findall(r'\w+', text))

def extract_provider_metadata(response_dict: Dict[str, Any]) -> str:
    """
    Reusable utility: Standardize metadata extraction from raw provider responses.
    """
    return response_dict.get("model", "unknown-model")
