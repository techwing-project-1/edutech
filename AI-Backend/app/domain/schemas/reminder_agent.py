from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from app.domain.schemas.notification import NotificationPriority, NotificationCategory

class ReminderType(str, Enum):
    ASSIGNMENT = "ASSIGNMENT"
    EXAM = "EXAM"
    REVISION = "REVISION"
    LAB = "LAB"
    PROJECT = "PROJECT"
    STUDY_SESSION = "STUDY_SESSION"
    FLASHCARD = "FLASHCARD"
    QUIZ = "QUIZ"
    STUDY_NOTES = "STUDY_NOTES"

class ReminderScheduleTime(str, Enum):
    ONE_HOUR = "ONE_HOUR"
    SIX_HOURS = "SIX_HOURS"
    TWELVE_HOURS = "TWELVE_HOURS"
    ONE_DAY = "ONE_DAY"
    TWO_DAYS = "TWO_DAYS"
    ONE_WEEK = "ONE_WEEK"
    CUSTOM = "CUSTOM"

class ReminderRequest(BaseModel):
    user_id: str = Field(..., description="Target user ID")
    department: Optional[str] = None
    semester: Optional[int] = None
    subject: Optional[str] = None
    section: Optional[str] = None
    schedule_time: ReminderScheduleTime = Field(ReminderScheduleTime.ONE_DAY, description="Default schedule buffer")

class ReminderPayload(BaseModel):
    title: str
    message: str
    category: NotificationCategory
    priority: NotificationPriority
    scheduled_for: str

class ReminderResponse(BaseModel):
    reminder_id: str
    user_id: str
    reminder_type: ReminderType
    reminder_time: str
    priority: NotificationPriority
    notification_payload: ReminderPayload
    status: str = Field("SCHEDULED", description="Status of reminder")
    
class ReminderListResponse(BaseModel):
    total: int
    reminders: List[ReminderResponse]
