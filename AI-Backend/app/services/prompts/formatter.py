from typing import Any
from app.core.exceptions import PromptException

class PromptFormatter:
    """
    Handles dynamic string replacement.
    Agnostic to the template source, solely responsible for injecting variables.
    """
    
    @staticmethod
    def format_template(template_str: str, **kwargs: Any) -> str:
        """Injects kwargs into the raw template string."""
        try:
            # Using Python's standard string formatting (Clean, no external dependencies)
            return template_str.format(**kwargs)
        except KeyError as e:
            raise PromptException(f"Prompt formatting failed. Missing dynamic key: {str(e)}")
        except Exception as e:
            raise PromptException(f"Unexpected prompt formatting error: {str(e)}")
