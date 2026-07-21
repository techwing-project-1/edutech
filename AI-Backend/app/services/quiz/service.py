import json
from typing import List

from app.domain.schemas.quiz import QuizRequest, QuizResponse, QuizQuestion, QuizType
from app.domain.schemas.content_generation import ContentGenerationRequest, GenerationMode, OutputFormat
from app.services.quiz.validator import QuizValidator
from app.services.content_generation.manager import ContentGenerationManager
from app.core.exceptions import QuizException, LLMReturnedInvalidJSON
from app.core.logger import logger
from app.utils.json_parser import SafeJsonParser
import uuid

class QuizService:
    """
    Service layer for generating quizzes.
    Validates input, maps to Content Generation Engine, and parses the structured JSON output.
    """
    
    def __init__(self):
        self.engine = ContentGenerationManager()

    async def generate_quiz(self, request: QuizRequest) -> QuizResponse:
        logger.info(f"QuizService processing request for topic: '{request.topic}'")
        
        try:
            # 1. Validate domain-specific quiz request
            QuizValidator.validate_request(request)

            # 2. Prepare Engine Request
            safe_max_tokens = min(4000, max(2000, request.number_of_questions * 400))
            
            engine_request = ContentGenerationRequest(
                topic=request.topic,
                mode=GenerationMode.QUIZ,
                department=request.department,
                semester=request.semester,
                subject=request.subject,
                section=request.section,
                output_format=OutputFormat.JSON, 
                language=request.language,
                creativity=request.creativity,
                max_tokens=safe_max_tokens, 
                additional_params={
                    "quiz_type": request.quiz_type.value,
                    "difficulty": request.difficulty.value,
                    "number_of_questions": request.number_of_questions
                }
            )

            # 3. Define Fallback Question
            fallback_question = QuizQuestion(
                question_id=f"q_fallback_{uuid.uuid4().hex[:8]}",
                question=f"Could not generate specific questions for {request.topic}. Please try again later.",
                question_type=QuizType.SHORT_ANSWER.value,
                difficulty=request.difficulty.value,
                options=[],
                correct_answer="N/A",
                explanation="This is a fallback placeholder due to an upstream generation issue.",
                topic=request.topic,
                source="System Fallback",
                page_number=None
            )

            # 4. Use Unified Strategy
            from app.services.content_generation.strategy import JsonArrayGeneratorStrategy
            strategy = JsonArrayGeneratorStrategy(self.engine)
            
            questions, metadata = await strategy.generate_json_array(
                request=engine_request,
                model_class=QuizQuestion,
                array_key="questions",
                max_attempts=3,
                id_field="question_id",
                id_prefix="q_",
                fallback_items=[fallback_question]
            )
            
            # Post-process missing question_type
            for q in questions:
                if getattr(q, 'question_type', None) is None:
                    q.question_type = request.quiz_type.value

            return QuizResponse(
                questions=questions,
                quiz_type=request.quiz_type,
                language=metadata.pop("language", request.language),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Quiz generation failed: {str(e)}")
            raise QuizException(f"Failed to generate quiz: {str(e)}")
