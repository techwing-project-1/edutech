from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.session import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, default="New Conversation")
    user_id = Column(String, index=True, nullable=False, default="default_user")
    status = Column(String, default="active")
    session_id = Column(String, index=True, nullable=True) # Optional session grouping
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    summary = Column(String, nullable=True) # For auto-summarization
    
    # Metadata for enterprise reporting
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    provider = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    default_model = Column(String, nullable=True)
    
    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at", lazy="selectin")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False) # 'user' or 'assistant' or 'system'
    content = Column(String, nullable=False)
    
    # Observability and Auditing fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Provider & LLM stats
    provider = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True) # Legacy alias
    latency_ms = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    response_id = Column(String, nullable=True)
    
    response_type = Column(String, nullable=True)
    language = Column(String, nullable=True)
    history_used = Column(Boolean, default=False)
    cached = Column(Boolean, default=False)
    processing_time = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)
    
    message_metadata = Column("metadata", JSON, nullable=True)
    
    conversation = relationship("Conversation", back_populates="messages", lazy="selectin")
