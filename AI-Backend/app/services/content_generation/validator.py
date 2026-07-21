from typing import Dict, Any
from app.domain.schemas.content_generation import ContentGenerationRequest, GenerationMode, OutputFormat
from app.core.exceptions import ContentValidationError, LLMReturnedInvalidJSON

class GeneratorValidator:
    """
    Validates input requests and output generation results for the Content Generation Engine.
    """
    
    @staticmethod
    def validate_request(request: ContentGenerationRequest) -> None:
        """
        Validates the incoming content generation request.
        """
        if not request.topic or not request.topic.strip():
            raise ContentValidationError("Topic cannot be empty")
            
        # Department, semester, and subject are Optional[str] in schema, 
        # so we don't strictly require them here to allow generic document chatting.
            
        if request.creativity < 0.0 or request.creativity > 1.0:
            raise ContentValidationError("Creativity must be between 0.0 and 1.0")
            
        if request.max_tokens <= 0:
            raise ContentValidationError("max_tokens must be positive")
            
        if request.mode not in [m.value for m in GenerationMode]:
            raise ContentValidationError(f"Invalid generation mode: {request.mode}")
            
        if request.output_format not in [f.value for f in OutputFormat]:
            raise ContentValidationError(f"Invalid output format: {request.output_format}")
            
        # Strategy specific format enforcement
        assessment_modes = [
            GenerationMode.FLASHCARDS, 
            GenerationMode.QUIZ, 
            GenerationMode.MCQS,
            GenerationMode.IMPORTANT_QUESTIONS
        ]
        
        if request.mode in assessment_modes and request.output_format == OutputFormat.PLAIN_TEXT:
            raise ContentValidationError(f"Mode {request.mode} requires structured output (JSON or MARKDOWN), got {request.output_format}")

    @staticmethod
    def validate_output(content: str, request: ContentGenerationRequest) -> None:
        """
        Validates the generated output based on the expected format and mode.
        """
        if not content or not content.strip():
            raise ContentValidationError("Generated content is empty")
            
        if request.output_format == OutputFormat.JSON:
            import json
            content_stripped = content.strip()
            
            if not content_stripped.startswith('{') and not content_stripped.startswith('['):
                raise LLMReturnedInvalidJSON(f"Content does not start with {{ or [. Raw content: {content}")
                
            try:
                # Basic validation to ensure it's a valid JSON string
                json.loads(content)
            except json.JSONDecodeError as e:
                raise LLMReturnedInvalidJSON(f"Generated content is not valid JSON: {str(e)}. Raw content: {content}")
