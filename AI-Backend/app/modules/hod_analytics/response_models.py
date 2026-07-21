from pydantic import BaseModel, Field
from typing import List, Optional

class PriorityAction(BaseModel):
    action: str
    impact: str

class HODAnalysisResponse(BaseModel):
    """Base response model for HOD Analysis outputs."""
    summary: str
    key_findings: List[str]
    strengths: List[str]
    weaknesses: List[str]
    risk_areas: List[str]
    recommendations: List[str]
    priority_actions: List[PriorityAction]
    overall_health_score: float = Field(..., description="A score from 0.0 to 100.0 representing department health.")
    
    metadata: dict = Field(default_factory=dict, description="Execution metadata including latency and provider used.")
