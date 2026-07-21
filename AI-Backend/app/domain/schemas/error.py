from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class APIErrorResponse(BaseModel):
    error_code: str = Field(..., description="Machine-readable error code")
    user_message: str = Field(..., description="Friendly error message for the user")
    developer_message: str = Field(..., description="Technical details of the error (no stack traces)")
    trace_id: str = Field(..., description="Unique request trace ID for debugging")
    retryable: bool = Field(False, description="Whether the client should retry the request")
    status: int = Field(..., description="HTTP status code")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
