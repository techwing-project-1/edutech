from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.domain.schemas.content_generation import OutputFormat

class SummaryType(str, Enum):
    SHORT = "SHORT"
    DETAILED = "DETAILED"
    BULLET_POINT = "BULLET_POINT"
    EXAM_REVISION = "EXAM_REVISION"
    CONCEPT = "CONCEPT"

class SummaryRequest(BaseModel):
    """
    Request model for generating a summary.
    """
    topic: str = Field(..., description="The main topic or question to summarize")
    summary_type: SummaryType = Field(SummaryType.SHORT, description="The type of summary to generate")
    department: Optional[str] = Field(None, description="Department context for RAG")
    semester: Optional[int] = Field(None, description="Semester context for RAG")
    subject: Optional[str] = Field(None, description="Subject context for RAG")
    section: Optional[str] = Field(None, description="Section context for RAG")
    output_format: OutputFormat = Field(OutputFormat.MARKDOWN, description="Format of the output")
    language: str = Field("English", description="Target language")
    length_words: int = Field(250, ge=50, le=2000, description="Target length of the summary in words")
    creativity: float = Field(0.5, ge=0.0, le=1.0, description="Creativity parameter")

class SummaryResponse(BaseModel):
    """
    Response model for a generated summary.
    """
    content: str = Field(..., description="The generated summary")
    summary_type: SummaryType = Field(..., description="The type of summary that was generated")
    format: OutputFormat = Field(..., description="Format of the response")
    language: str = Field(..., description="Language used")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used from RAG")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata like tokens, latency, provider")
