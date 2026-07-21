from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SubjectPerformance(BaseModel):
    subject_name: str
    average_marks: float
    pass_percentage: float

class FacultyStat(BaseModel):
    faculty_name: str
    classes_taken: int
    materials_uploaded: int

class AnalyticsPayload(BaseModel):
    department_name: str
    semester: str
    student_count: int
    attendance_percentage: float
    assignment_completion_rate: float
    average_marks: float
    subject_performance: List[SubjectPerformance]
    faculty_stats: List[FacultyStat]
    at_risk_students_count: int
    course_completion_percentage: float

class HODAnalyticsRequest(BaseModel):
    """Request model for HOD Analytics endpoints, designed to be passed from the Orchestrator."""
    user_id: Optional[str] = None
    query: Optional[str] = "Analyze this department data"
    data: AnalyticsPayload

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "hod-123",
                "query": "Give me a summary of the department",
                "data": {
                    "department_name": "Computer Science",
                    "semester": "Fall 2026",
                    "student_count": 250,
                    "attendance_percentage": 85.5,
                    "assignment_completion_rate": 90.0,
                    "average_marks": 78.5,
                    "subject_performance": [
                        {"subject_name": "Data Structures", "average_marks": 82.0, "pass_percentage": 95.0},
                        {"subject_name": "Operating Systems", "average_marks": 65.0, "pass_percentage": 70.0}
                    ],
                    "faculty_stats": [
                        {"faculty_name": "Dr. Smith", "classes_taken": 40, "materials_uploaded": 15},
                        {"faculty_name": "Prof. Johnson", "classes_taken": 35, "materials_uploaded": 5}
                    ],
                    "at_risk_students_count": 12,
                    "course_completion_percentage": 92.5
                }
            }
        }
    }
