from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timezone

class NotificationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class NotificationCategory(str, Enum):
    ASSIGNMENT = "ASSIGNMENT"
    EXAM = "EXAM"
    REVISION = "REVISION"
    STUDY_PLAN = "STUDY_PLAN"
    QUIZ = "QUIZ"
    FLASHCARDS = "FLASHCARDS"
    STUDY_NOTES = "STUDY_NOTES"
    SYSTEM = "SYSTEM"

class DeliveryType(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    WEBHOOK = "WEBHOOK"

class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    READ = "READ"

class NotificationRequest(BaseModel):
    user_id: str = Field(..., description="Target user ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification body content")
    category: NotificationCategory = Field(..., description="Notification category")
    priority: NotificationPriority = Field(NotificationPriority.MEDIUM, description="Priority level")
    delivery_types: List[DeliveryType] = Field([DeliveryType.IN_APP], description="Requested delivery methods")
    scheduled_for: Optional[str] = Field(None, description="ISO 8601 schedule time")
    expires_at: Optional[str] = Field(None, description="ISO 8601 expiration time")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

class BulkNotificationRequest(BaseModel):
    requests: List[NotificationRequest] = Field(..., description="List of notification requests")

class NotificationResponse(BaseModel):
    notification_id: str = Field(..., description="Unique notification ID")
    user_id: str = Field(..., description="Target user ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification body content")
    category: NotificationCategory
    priority: NotificationPriority
    status: NotificationStatus
    delivery_types: List[DeliveryType]
    created_at: str
    scheduled_for: Optional[str]
    expires_at: Optional[str]
    metadata: Dict[str, Any]
    retry_count: int = Field(0, description="Number of times retried")

class NotificationListResponse(BaseModel):
    total: int
    notifications: List[NotificationResponse]

class NotificationUpdateResponse(BaseModel):
    success: bool
    notification_id: str
    status: NotificationStatus
