from typing import Dict
from app.domain.schemas.prompt import PromptTemplateSchema
from app.core.exceptions import PromptException
from app.core.logger import logger

class PromptRegistry:
    """
    Centralized in-memory registry for prompt schemas.
    Allows dynamic lookup of prompt metadata and paths by template name.
    Supports seamless prompt versioning by registering different names (e.g., 'quiz_v1', 'quiz_v2').
    """
    _templates: Dict[str, PromptTemplateSchema] = {}

    @classmethod
    def register(cls, schema: PromptTemplateSchema):
        """Registers a prompt template into the system."""
        cls._templates[schema.name] = schema
        logger.debug(f"Registered Prompt Template: {schema.name}")

    @classmethod
    def get(cls, name: str) -> PromptTemplateSchema:
        """Retrieves a registered prompt schema."""
        if name not in cls._templates:
            raise PromptException(f"Prompt template '{name}' is not registered.")
        return cls._templates[name]
