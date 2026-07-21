from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AssignmentItem(BaseModel):
    assignment_id: str = Field(..., description="A unique identifier for the assignment")
    title: str = Field(..., description="Title of the assignment, project, or exam")
    subject: str = Field(..., description="Subject of the assignment")
    department: Optional[str] = Field(None, description="Department context")
    semester: Optional[int] = Field(None, description="Semester context")
    section: Optional[str] = Field(None, description="Section context")
    due_date: Optional[str] = Field(None, description="Detected due date or schedule")
    description: str = Field(..., description="Description or instructions for the assignment")
    priority: str = Field("Normal", description="Priority based on text context (High, Normal, Low)")
    confidence_score: float = Field(..., description="Confidence score from 0.0 to 1.0")

class AssignmentAgentRequest(BaseModel):
    """Request model for the assignment agent."""
    user_id: str = Field(..., description="The ID of the student")
    department: Optional[str] = Field(None, description="Department context for RAG")
    semester: Optional[int] = Field(None, description="Semester context for RAG")
    subject: Optional[str] = Field(None, description="Subject context for RAG")
    section: Optional[str] = Field(None, description="Section context for RAG")

class AssignmentAgentResponse(BaseModel):
    """Response model for the assignment agent."""
    assignments: List[AssignmentItem] = Field(default_factory=list, description="Extracted assignments")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used from RAG")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
