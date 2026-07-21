from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class StudyIntensity(str, Enum):
    LIGHT = "LIGHT"
    NORMAL = "NORMAL"
    INTENSIVE = "INTENSIVE"

class StudyPlannerRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the student")
    department: Optional[str] = Field(None, description="Department context")
    semester: Optional[int] = Field(None, description="Semester context")
    subject: Optional[str] = Field(None, description="Subject context")
    section: Optional[str] = Field(None, description="Section context")
    study_hours_per_day: float = Field(2.0, ge=0.5, le=16.0, description="Daily study hours")
    study_intensity: StudyIntensity = Field(StudyIntensity.NORMAL, description="Intensity of study plan")
    preferred_study_timings: str = Field("Evening", description="Preferred timings (e.g., Morning, Evening, Night)")

class DailyPlan(BaseModel):
    date: str = Field(..., description="Date of the plan")
    targets: List[str] = Field(default_factory=list, description="List of learning targets for the day")
    hours_allocated: float = Field(..., description="Hours allocated for the day")

class WeeklyPlan(BaseModel):
    week_number: int = Field(..., description="Week number")
    milestones: List[str] = Field(default_factory=list, description="Weekly milestones to achieve")
    daily_plans: List[DailyPlan] = Field(default_factory=list, description="Daily plans for the week")

class StudyPlannerResponse(BaseModel):
    planner_id: str = Field(..., description="Generated planner ID")
    daily_plan: List[DailyPlan] = Field(default_factory=list, description="Daily plans")
    weekly_plan: List[WeeklyPlan] = Field(default_factory=list, description="Weekly plans")
    monthly_plan: List[str] = Field(default_factory=list, description="Monthly goals/plans")
    revision_schedule: List[str] = Field(default_factory=list, description="Revision schedule overview")
    exam_preparation: List[str] = Field(default_factory=list, description="Exam preparation strategy")
    lab_preparation: List[str] = Field(default_factory=list, description="Lab preparation plan")
    project_roadmap: List[str] = Field(default_factory=list, description="Project completion roadmap")
    study_hours: float = Field(..., description="Total or daily average study hours")
    break_suggestions: List[str] = Field(default_factory=list, description="Break recommendations")
    completion_estimate: str = Field(..., description="Estimate of completion date or readiness")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
