from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, description="New title for the conversation")
    is_pinned: Optional[bool] = Field(None, description="Pin or unpin the conversation")
    is_archived: Optional[bool] = Field(None, description="Archive or unarchive the conversation")

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the sender: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class GeneralAIRequest(BaseModel):
    """
    Request model for the General AI Chat endpoint.
    Independent of RAG.
    """
    session_id: Optional[str] = Field(None, description="Unique session ID for tracking history")
    conversation_id: Optional[str] = Field(None, description="Unique ID for resuming an existing conversation")
    query: str = Field(..., max_length=4096, description="The user's query")
    history: List[ChatMessage] = Field(default_factory=list, description="Previous conversation history (optional, now handled by DB if conversation_id provided)")
    stream: bool = Field(False, description="Whether to stream the response via SSE")
    
    # Configurable LLM Parameters
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2048, ge=1, le=8192, description="Maximum tokens to generate")
    provider_name: Optional[str] = Field(None, description="Specific provider to use (default: Primary Provider)")
    model_name: Optional[str] = Field(None, description="Specific model to use (default: Provider's default)")

from app.domain.schemas.llm import TokenUsage

class GeneralAIResponse(BaseModel):
    """
    Response model for the General AI Chat endpoint.
    """
    answer: str = Field(..., description="The generated response text")
    provider_used: str = Field(..., description="The name of the provider that generated the response")
    model_name: str = Field(..., description="The exact model version used")
    latency_ms: int = Field(..., description="Time taken to generate the response in milliseconds")
    fallback_used: bool = Field(False, description="Whether a fallback provider was used")
    usage: TokenUsage = Field(..., description="Token usage statistics")
    cost: Optional[float] = Field(0.0, description="Estimated cost of this request")

    # Conversation tracking — returned so client can use for GET /conversations/{id}
    conversation_id: Optional[str] = Field(None, description="The conversation ID — use for subsequent GET /conversations/{id} calls")
    message_id: Optional[str] = Field(None, description="The unique ID of the assistant message just created")

    response_type: Optional[str] = Field("General", description="Classified intent or category")
    language: Optional[str] = Field("en", description="Language of response")
    history_used: bool = Field(False, description="Was history used")
    cached: bool = Field(False, description="Was response served from cache")
    processing_time: Optional[int] = Field(None, description="Internal processing time outside LLM")
    confidence: Optional[float] = Field(None, description="Confidence of response")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    session_id: Optional[str] = Field(None, description="Session ID tracking")
    response_id: Optional[str] = Field(None, description="Unique response ID")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "Hello! I am a helpful AI assistant.",
                "provider_used": "Google Gemini",
                "model_name": "gemini-2.5-flash",
                "latency_ms": 450,
                "fallback_used": False,
                "usage": {
                    "prompt_tokens": 15,
                    "completion_tokens": 10,
                    "total_tokens": 25
                },
                "cost": 0.002,
                "conversation_id": "conv-uuid-here",
                "message_id": "msg-uuid-here",
                "timestamp": "2026-07-16T12:00:00Z",
                "session_id": "sess-123",
                "response_id": "resp-456"
            }
        }
    }

class MessageUpdate(BaseModel):
    content: str = Field(..., description="New message content to update the AI's or user's prompt")

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    provider: Optional[str] = None
    model_name: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    cached: Optional[bool] = None
    response_type: Optional[str] = None
    language: Optional[str] = None
    
    class Config:
        from_attributes = True

class ConversationDetail(BaseModel):
    id: str
    title: str
    status: str
    session_id: Optional[str] = None
    summary: Optional[str] = None
    is_pinned: bool = False
    is_archived: bool = False
    provider: Optional[str] = None
    model_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None   # Optional — NULL on legacy/fresh rows
    last_message_at: Optional[datetime] = None
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

