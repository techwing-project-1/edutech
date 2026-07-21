from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.domain.schemas.content_generation import OutputFormat

class NoteType(str, Enum):
    BEGINNER = "BEGINNER"
    DETAILED = "DETAILED"
    EXAM_REVISION = "EXAM_REVISION"
    QUICK_REVISION = "QUICK_REVISION"
    BULLET = "BULLET"
    CONCEPT = "CONCEPT"
    FORMULA_KEY_POINTS = "FORMULA_KEY_POINTS"

class StudyNotesRequest(BaseModel):
    """
    Request model for generating study notes.
    """
    topic: str = Field(..., description="The main topic or question to generate notes for")
    note_type: NoteType = Field(NoteType.DETAILED, description="The type of study notes to generate")
    department: Optional[str] = Field(None, description="Department context for RAG")
    semester: Optional[int] = Field(None, description="Semester context for RAG")
    subject: Optional[str] = Field(None, description="Subject context for RAG")
    section: Optional[str] = Field(None, description="Section context for RAG")
    output_format: OutputFormat = Field(OutputFormat.MARKDOWN, description="Format of the output")
    language: str = Field("English", description="Target language")
    length_words: int = Field(500, ge=100, le=4000, description="Target length of the notes in words")
    creativity: float = Field(0.5, ge=0.0, le=1.0, description="Creativity parameter")
    include_mermaid: bool = Field(False, description="Flag to include Mermaid diagrams if applicable")

class StudyNotesResponse(BaseModel):
    """
    Response model for generated study notes.
    """
    content: str = Field(..., description="The generated study notes")
    note_type: NoteType = Field(..., description="The type of notes that were generated")
    format: OutputFormat = Field(..., description="Format of the response")
    language: str = Field(..., description="Language used")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used from RAG")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata like tokens, latency, provider")
