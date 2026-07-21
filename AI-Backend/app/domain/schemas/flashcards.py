from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.domain.schemas.content_generation import OutputFormat

class FlashcardType(str, Enum):
    DEFINITION = "DEFINITION"
    CONCEPT = "CONCEPT"
    QUESTION_ANSWER = "QUESTION_ANSWER"
    FORMULA = "FORMULA"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_IN_BLANK = "FILL_IN_BLANK"

class FlashcardDifficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class FlashcardItem(BaseModel):
    """
    Represents a single generated flashcard.
    """
    card_id: str = Field(..., description="Unique identifier for the flashcard")
    question: str = Field(..., description="The front of the flashcard")
    answer: str = Field(..., description="The back of the flashcard")
    difficulty: FlashcardDifficulty = Field(..., description="Difficulty level of the flashcard")
    topic: str = Field(..., description="Specific topic the flashcard belongs to")
    source: str = Field(..., description="Source document or reference")
    page_number: Optional[int] = Field(None, description="Page number reference if available")

class FlashcardRequest(BaseModel):
    """
    Request model for generating flashcards.
    """
    topic: str = Field(..., description="The main topic or query for flashcard generation")
    flashcard_type: FlashcardType = Field(FlashcardType.QUESTION_ANSWER, description="Type of flashcards to generate")
    difficulty: FlashcardDifficulty = Field(FlashcardDifficulty.MEDIUM, description="Target difficulty level")
    number_of_cards: int = Field(5, ge=1, le=50, description="Number of flashcards to generate")
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
                "topic": "Newton's Laws of Motion",
                "flashcard_type": "QUESTION_ANSWER",
                "difficulty": "MEDIUM",
                "number_of_cards": 5,
                "department": "Physics",
                "output_format": "JSON",
                "language": "English",
                "creativity": 0.5
            }
        }
    }

class FlashcardResponse(BaseModel):
    """
    Response model containing generated flashcards.
    """
    flashcards: List[FlashcardItem] = Field(..., description="The generated flashcards")
    flashcard_type: FlashcardType = Field(..., description="The type of flashcards generated")
    language: str = Field(..., description="Language used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata like tokens, latency, provider")
