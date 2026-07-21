from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class EventCategory(str, Enum):
    ASSIGNMENT = "ASSIGNMENT"
    REVISION = "REVISION"
    EXAM = "EXAM"
    LAB = "LAB"
    PROJECT = "PROJECT"
    REMINDER = "REMINDER"

class CalendarEvent(BaseModel):
    event_id: str = Field(..., description="Unique ID for the event")
    title: str = Field(..., description="Title of the event")
    description: str = Field("", description="Detailed description")
    start_date: str = Field(..., description="ISO 8601 start date and time")
    end_date: str = Field(..., description="ISO 8601 end date and time")
    priority: str = Field("Normal", description="High, Normal, Low")
    category: EventCategory = Field(..., description="Category of event")
    color_tag: str = Field("#3788d8", description="Hex color code for UI rendering")
    recurring: bool = Field(False, description="Flag for recurring events")
    recurrence_rule: Optional[str] = Field(None, description="RRULE string for recurrences")
    reminders: List[int] = Field(default_factory=list, description="Minutes before event to remind")

class CalendarAgentRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the student")
    department: Optional[str] = Field(None, description="Department context")
    semester: Optional[int] = Field(None, description="Semester context")
    subject: Optional[str] = Field(None, description="Subject context")
    section: Optional[str] = Field(None, description="Section context")

class CalendarAgentResponse(BaseModel):
    calendar_id: str = Field(..., description="Generated calendar ID")
    events: List[CalendarEvent] = Field(default_factory=list, description="List of generated structured events")
    ics_file: str = Field(..., description="String containing the raw ICS file format")
    json_events: str = Field(..., description="String containing the raw JSON formatted events")
    statistics: Dict[str, int] = Field(default_factory=dict, description="Stats like total events, by category, etc.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
