from pydantic import BaseModel, Field
from typing import List
from app.services.prompts.constants import PromptCategory, PromptType

class PromptMetadata(BaseModel):
    """
    Metadata for tracking prompt versioning, categorizations, and authors.
    Essential for A/B testing and production analytics.
    """
    category: PromptCategory
    version: str = Field(default="1.0.0")
    description: str
    author: str = Field(default="system")
    tags: List[str] = Field(default_factory=list)

class PromptTemplateSchema(BaseModel):
    """
    Defines the structural contract of a prompt template.
    Ensures that dynamic variables are tracked and validated before formatting.
    """
    name: str = Field(..., description="Unique identifier for the prompt template (e.g. general_ai_system_v1)")
    prompt_type: PromptType
    metadata: PromptMetadata
    template_path: str = Field(..., description="File path to the raw text/markdown prompt file")
    variables: List[str] = Field(default_factory=list, description="List of expected format variables")
