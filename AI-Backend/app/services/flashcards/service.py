import json
from typing import List

from app.domain.schemas.flashcards import FlashcardRequest, FlashcardResponse, FlashcardItem
from app.domain.schemas.content_generation import ContentGenerationRequest, GenerationMode, OutputFormat
from app.services.flashcards.validator import FlashcardValidator
from app.services.content_generation.manager import ContentGenerationManager
from app.core.exceptions import FlashcardException
from app.core.logger import logger

class FlashcardService:
    """
    Service layer for generating flashcards.
    Validates input, maps to Content Generation Engine, and parses the structured JSON output.
    """
    
    def __init__(self):
        self.engine = ContentGenerationManager()

    async def generate_flashcards(self, request: FlashcardRequest) -> FlashcardResponse:
        logger.info(f"FlashcardService processing request for topic: '{request.topic}'")
        
        try:
            # 1. Validate domain-specific flashcard request
            FlashcardValidator.validate_request(request)

            # 2. Prepare Engine Request
            safe_max_tokens = min(4000, max(1500, request.number_of_cards * 350))
            
            engine_request = ContentGenerationRequest(
                topic=request.topic,
                mode=GenerationMode.FLASHCARDS,
                department=request.department,
                semester=request.semester,
                subject=request.subject,
                section=request.section,
                output_format=OutputFormat.JSON, 
                language=request.language,
                creativity=request.creativity,
                max_tokens=safe_max_tokens, 
                additional_params={
                    "flashcard_type": request.flashcard_type.value,
                    "difficulty": request.difficulty.value,
                    "number_of_cards": request.number_of_cards
                }
            )

            # 3. Define Fallback Flashcard
            import uuid
            fallback_flashcard = FlashcardItem(
                card_id=f"fc_fallback_{uuid.uuid4().hex[:8]}",
                question=f"Could not generate flashcards for {request.topic}.",
                answer="Please try again later. This is a system fallback.",
                difficulty=request.difficulty.value,
                topic=request.topic,
                source="System Fallback"
            )

            # 4. Use Unified Strategy
            from app.services.content_generation.strategy import JsonArrayGeneratorStrategy
            strategy = JsonArrayGeneratorStrategy(self.engine)
            
            flashcards, metadata = await strategy.generate_json_array(
                request=engine_request,
                model_class=FlashcardItem,
                array_key="flashcards",
                max_attempts=2,
                id_field="card_id",
                id_prefix="fc_",
                fallback_items=[fallback_flashcard]
            )
            
            return FlashcardResponse(
                flashcards=flashcards,
                flashcard_type=request.flashcard_type,
                language=metadata.pop("language", request.language),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Flashcard generation failed: {str(e)}")
            from app.core.exceptions import EmptyContextError, LLMReturnedInvalidJSON
            if isinstance(e, EmptyContextError):
                raise e
            if isinstance(e, LLMReturnedInvalidJSON):
                raise e
            raise FlashcardException(f"Failed to generate flashcards: {str(e)}")
