from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class GenerationMode(str, Enum):
    SUMMARY = "SUMMARY"
    FLASHCARDS = "FLASHCARDS"
    QUIZ = "QUIZ"
    STUDY_NOTES = "STUDY_NOTES"
    IMPORTANT_QUESTIONS = "IMPORTANT_QUESTIONS"
    MCQS = "MCQS"
    SHORT_NOTES = "SHORT_NOTES"
    LONG_NOTES = "LONG_NOTES"

class OutputFormat(str, Enum):
    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    PLAIN_TEXT = "PLAIN_TEXT"
    BULLET_POINTS = "BULLET_POINTS"
    TABLES = "TABLES"

class ContentGenerationRequest(BaseModel):
    """
    Standard request model for AI Content Generation.
    Supports configuration for mode, format, language, and creativity.
    """
    topic: str = Field(..., min_length=1, max_length=1000, description="The main topic or query for content generation")
    mode: GenerationMode = Field(..., description="The type of content to generate")
    document_id: Optional[str] = Field(None, max_length=255, description="Specific document ID to chat with exclusively")
    department: Optional[str] = Field(None, max_length=100, description="Department context for RAG retrieval")
    semester: Optional[int] = Field(None, ge=1, le=10, description="Semester context for RAG retrieval")
    subject: Optional[str] = Field(None, max_length=100, description="Subject context for RAG retrieval")
    section: Optional[str] = Field(None, max_length=100, description="Section context for RAG retrieval")
    output_format: OutputFormat = Field(OutputFormat.MARKDOWN, description="Desired output format")
    language: str = Field("English", max_length=50, description="Target language for the generated content")
    creativity: float = Field(0.7, ge=0.0, le=1.0, description="Temperature/Creativity level (0.0 to 1.0)")
    max_tokens: int = Field(2048, ge=100, le=32000, description="Maximum tokens for the generated response")
    additional_params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters specific to the mode")

class ContentGenerationResponse(BaseModel):
    """
    Standard response model for AI Content Generation.
    """
    content: str = Field(..., description="The generated content in the requested format")
    mode: GenerationMode = Field(..., description="The mode that was used for generation")
    format: OutputFormat = Field(..., description="The format of the returned content")
    language: str = Field(..., description="The language of the generated content")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used from RAG")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the generation process (e.g. latency, provider)")
