import os
import functools
from app.core.exceptions import PromptException
from app.core.logger import logger

class PromptLoader:
    """
    Dedicated component to load prompt templates from the filesystem.
    Ensures prompts are never hardcoded in Python logic, enforcing strict separation of concerns.
    """
    
    @staticmethod
    @functools.lru_cache(maxsize=32)
    def load_template(filepath: str) -> str:
        """Reads a prompt template from a dedicated text/markdown file."""
        if not os.path.exists(filepath):
            logger.error(f"Prompt template file not found: {filepath}")
            raise PromptException(f"Prompt template not found at {filepath}")
            
        try:
            with open(filepath, mode='r', encoding='utf-8') as f:
                content = f.read()
                return content.strip()
        except Exception as e:
            logger.error(f"Failed to load prompt template {filepath}: {str(e)}")
            raise PromptException(f"Failed to load template: {str(e)}")
