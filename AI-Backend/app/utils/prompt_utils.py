import re

def clean_prompt_whitespace(prompt: str) -> str:
    """
    Reusable utility: Cleans up excessive newlines or whitespace from a dynamically formatted prompt.
    Ensures optimal token usage.
    """
    return re.sub(r'\n{3,}', '\n\n', prompt).strip()
