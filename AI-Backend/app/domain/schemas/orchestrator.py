from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class AIMode(str, Enum):
    COURSE_RAG = "COURSE_RAG"
    GENERAL_AI = "GENERAL_AI"
    FLASHCARDS = "FLASHCARDS"
    SUMMARY = "SUMMARY"
    QUIZ = "QUIZ"
    STUDY_NOTES = "STUDY_NOTES"
    ASSIGNMENT = "ASSIGNMENT"
    CALENDAR = "CALENDAR"
    PLANNER = "PLANNER"
    REMINDER = "REMINDER"
    HOD_ANALYTICS = "HOD_ANALYTICS"
    DEPARTMENT_REPORT = "DEPARTMENT_REPORT"
    RISK_ANALYSIS = "RISK_ANALYSIS"
    NOTIFICATION = "NOTIFICATION"

class OrchestratorRequest(BaseModel):
    user_id: str = Field(..., description="Target user ID")
    mode: Optional[AIMode] = Field(None, description="Explicit mode. If not provided, it will be auto-detected.")
    query: Optional[str] = Field(None, description="User query for mode detection or RAG/General execution")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Payload for the target service")

class NormalizedResponse(BaseModel):
    success: bool
    message: str
    data: Any
    metadata: Dict[str, Any]
    timestamp: str
    request_id: str
    execution_time: float
    error: Optional[str] = None
