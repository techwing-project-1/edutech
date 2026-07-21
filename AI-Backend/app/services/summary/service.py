from app.domain.schemas.summary import SummaryRequest, SummaryResponse
from app.domain.schemas.content_generation import ContentGenerationRequest, GenerationMode
from app.services.summary.validator import SummaryValidator
from app.services.content_generation.manager import ContentGenerationManager
from app.core.exceptions import SummaryException
from app.core.logger import logger

class SummaryService:
    """
    Service layer for generating summaries.
    Validates input and maps it to the unified Content Generation Engine.
    """
    
    def __init__(self):
        self.engine = ContentGenerationManager()

    async def generate_summary(self, request: SummaryRequest) -> SummaryResponse:
        logger.info(f"SummaryService processing request for topic: '{request.topic}'")
        
        try:
            # 1. Validate domain-specific summary request
            SummaryValidator.validate_request(request)

            # 2. Map to unified ContentGenerationRequest
            engine_request = ContentGenerationRequest(
                topic=request.topic,
                mode=GenerationMode.SUMMARY,
                department=request.department,
                semester=request.semester,
                subject=request.subject,
                section=request.section,
                output_format=request.output_format,
                language=request.language,
                creativity=request.creativity,
                # Maximum tokens a summary might need, although length_words dictates actual length
                max_tokens=request.length_words * 4, 
                additional_params={
                    "summary_type": request.summary_type.value,
                    "length_words": request.length_words
                }
            )

            # 3. Delegate to Content Generation Engine
            engine_response = await self.engine.generate_content(engine_request)

            # 4. Map back to domain-specific SummaryResponse
            return SummaryResponse(
                content=engine_response.content,
                summary_type=request.summary_type,
                format=engine_response.format,
                language=engine_response.language,
                sources=engine_response.sources,
                metadata=engine_response.metadata
            )
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            raise SummaryException(f"Failed to generate summary: {str(e)}")
