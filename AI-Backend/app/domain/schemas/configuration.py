from pydantic import BaseModel, Field
from typing import Dict, Any, List
from enum import Enum

class EnvironmentProfile(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"

class FeatureFlag(str, Enum):
    COURSE_RAG = "COURSE_RAG"
    GENERAL_AI = "GENERAL_AI"
    SUMMARY = "SUMMARY"
    FLASHCARDS = "FLASHCARDS"
    QUIZ = "QUIZ"
    STUDY_NOTES = "STUDY_NOTES"
    ASSIGNMENT_AGENT = "ASSIGNMENT_AGENT"
    CALENDAR_AGENT = "CALENDAR_AGENT"
    STUDY_PLANNER = "STUDY_PLANNER"
    REMINDER_AGENT = "REMINDER_AGENT"
    MONITORING = "MONITORING"
    OPENCLAW = "OPENCLAW"

class ProviderConfigModel(BaseModel):
    primary_provider: str
    fallback_enabled: bool
    default_timeout: float
    retry_count: int

class VectorDBConfigModel(BaseModel):
    provider: str
    host: str
    port: int

class SystemConfiguration(BaseModel):
    environment: EnvironmentProfile
    providers: ProviderConfigModel
    vector_db: VectorDBConfigModel
    agents: Dict[str, Any]
    models: Dict[str, str]

class FeatureUpdateRequest(BaseModel):
    enabled: bool

class FeatureResponse(BaseModel):
    feature: FeatureFlag
    enabled: bool

class ConfigurationResponse(BaseModel):
    configuration: SystemConfiguration
    features: Dict[FeatureFlag, bool]
