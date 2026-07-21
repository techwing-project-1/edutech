from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.domain.schemas.content_generation import OutputFormat

class QuizType(str, Enum):
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_IN_BLANKS = "FILL_IN_BLANKS"
    SHORT_ANSWER = "SHORT_ANSWER"
    LONG_ANSWER = "LONG_ANSWER"
    CASE_STUDY = "CASE_STUDY"
    MIXED = "MIXED"

class QuizDifficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    MIXED = "MIXED"

class QuizQuestion(BaseModel):
    """
    Represents a single generated quiz question.
    """
    question_id: str = Field(..., description="Unique identifier for the question")
    question: str = Field(..., description="The actual question text")
    question_type: str = Field(..., description="Type of the question (e.g. MULTIPLE_CHOICE, SHORT_ANSWER)")
    difficulty: str = Field(..., description="Difficulty level of the question")
    options: Optional[List[str]] = Field(None, description="List of options if MULTIPLE_CHOICE")
    correct_answer: str = Field(..., description="The correct answer to the question")
    explanation: str = Field(..., description="Explanation of why the correct answer is correct")
    topic: str = Field(..., description="Specific topic the question belongs to")
    source: str = Field(..., description="Source document or reference")
    page_number: Optional[int] = Field(None, description="Page number reference if available")

class QuizRequest(BaseModel):
    """
    Request model for generating a quiz.
    """
    topic: str = Field(..., description="The main topic or query for quiz generation")
    quiz_type: QuizType = Field(QuizType.MULTIPLE_CHOICE, description="Type of quiz questions to generate")
    difficulty: QuizDifficulty = Field(QuizDifficulty.MEDIUM, description="Target difficulty level")
    number_of_questions: int = Field(10, ge=1, le=50, description="Number of questions to generate")
    department: Optional[str] = Field(None, description="Department context for RAG")
    semester: Optional[int] = Field(None, description="Semester context for RAG")
    subject: Optional[str] = Field(None, description="Subject context for RAG")
    section: Optional[str] = Field(None, description="Section context for RAG")
    output_format: OutputFormat = Field(OutputFormat.JSON, description="Requested output format (usually JSON for structured)")
    language: str = Field("English", description="Target language")
    creativity: float = Field(0.5, ge=0.0, le=1.0, description="Creativity parameter")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "topic": "Photosynthesis",
                "quiz_type": "MULTIPLE_CHOICE",
                "difficulty": "MEDIUM",
                "number_of_questions": 5,
                "department": "Biology",
                "output_format": "JSON",
                "language": "English",
                "creativity": 0.5
            }
        }
    }

class QuizResponse(BaseModel):
    """
    Response model containing generated quiz questions.
    """
    questions: List[QuizQuestion] = Field(..., description="The generated quiz questions")
    quiz_type: QuizType = Field(..., description="The type of quiz generated")
    language: str = Field(..., description="Language used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata like tokens, latency, provider")
