from app.domain.schemas.study_notes import StudyNotesRequest, StudyNotesResponse
from app.domain.schemas.content_generation import ContentGenerationRequest, GenerationMode
from app.services.study_notes.validator import StudyNotesValidator
from app.services.content_generation.manager import ContentGenerationManager
from app.core.exceptions import StudyNotesException, StudyNotesValidationError
from app.core.logger import logger

class StudyNotesService:
    """
    Service layer for generating study notes.
    Validates input and maps it to the unified Content Generation Engine.
    """
    
    def __init__(self):
        self.engine = ContentGenerationManager()

    async def generate_notes(self, request: StudyNotesRequest) -> StudyNotesResponse:
        logger.info(f"StudyNotesService processing request for topic: '{request.topic}'")
        
        try:
            # 1. Validate domain-specific study notes request
            StudyNotesValidator.validate_request(request)

            # 2. Map to unified ContentGenerationRequest
            engine_request = ContentGenerationRequest(
                topic=request.topic,
                mode=GenerationMode.STUDY_NOTES,
                department=request.department,
                semester=request.semester,
                subject=request.subject,
                section=request.section,
                output_format=request.output_format,
                language=request.language,
                creativity=request.creativity,
                max_tokens=int(request.length_words * 4), 
                additional_params={
                    "note_type": request.note_type.value,
                    "length_words": request.length_words,
                    "include_mermaid": request.include_mermaid
                }
            )

            # 3. Delegate to Content Generation Engine
            engine_response = await self.engine.generate_content(engine_request)

            # 4. Map back to domain-specific StudyNotesResponse
            return StudyNotesResponse(
                content=engine_response.content,
                note_type=request.note_type,
                format=engine_response.format,
                language=engine_response.language,
                sources=engine_response.sources,
                metadata=engine_response.metadata
            )
            
        except StudyNotesValidationError as e:
            logger.error(f"Study notes validation failed: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Study notes generation failed: {str(e)}")
            raise StudyNotesException(f"Failed to generate study notes: {str(e)}")
