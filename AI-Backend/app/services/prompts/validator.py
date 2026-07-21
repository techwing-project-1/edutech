from typing import Dict, Any
from app.domain.schemas.prompt import PromptTemplateSchema
from app.core.exceptions import PromptException

class PromptValidator:
    """
    Validates dynamic prompt variables before they are formatted into the template.
    Prevents runtime KeyError exceptions during formatting.
    """
    
    @staticmethod
    def validate_variables(schema: PromptTemplateSchema, kwargs: Dict[str, Any]) -> None:
        """Ensures all required variables exist in the provided kwargs."""
        missing_vars = [var for var in schema.variables if var not in kwargs]
        
        if missing_vars:
            raise PromptException(
                f"Missing required prompt variables: {missing_vars} "
                f"for template '{schema.name}'. Expected: {schema.variables}"
            )
