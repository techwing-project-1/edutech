from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar("T")

class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class StandardAPIResponse(BaseModel, Generic[T]):
    status: str = Field(..., description="SUCCESS or ERROR")
    message: str = Field(..., description="Human-readable message")
    request_id: str = Field(..., description="Unique trace ID for the request")
    execution_time: float = Field(..., description="Time taken in milliseconds")
    data: Optional[T] = Field(None, description="The generic payload data")
    errors: Optional[List[APIError]] = Field(None, description="List of errors if status is ERROR")
