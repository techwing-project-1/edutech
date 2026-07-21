from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, desc, asc, exists
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm.attributes import set_committed_value
from app.domain.models.conversation import Conversation, Message
from app.core.logger import logger

class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_conversation(self, session_id: Optional[str] = None, title: str = "New Conversation", user_id: str = "default_user") -> Conversation:
        conversation = Conversation(session_id=session_id, title=title, user_id=user_id)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        # Initialize empty collections safely to avoid lazy loading trigger and collection replace events
        set_committed_value(conversation, 'messages', [])
        logger.info(f"[ConversationRepository] Created new conversation id={conversation.id} session_id={session_id}")
        return conversation

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        result = await self.session.execute(
            select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id)
        )
        return result.scalars().first()

    async def get_recent_conversations(self, limit: int = 20) -> List[Conversation]:
        result = await self.session.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.is_archived == False)
            .order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_conversations(
        self,
        keyword: Optional[str] = None,
        provider: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        stmt = select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.is_archived == False)
        
        if keyword:
            # Search title, summary, AND message content for comprehensive discovery
            message_content_match = select(Message.id).where(
                Message.conversation_id == Conversation.id,
                Message.content.ilike(f"%{keyword}%")
            ).exists()
            stmt = stmt.where(or_(
                Conversation.title.ilike(f"%{keyword}%"),
                Conversation.summary.ilike(f"%{keyword}%"),
                message_content_match
            ))
            
        if provider:
            stmt = stmt.where(Conversation.provider == provider)
            
        stmt = stmt.order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        convs = list(result.scalars().unique().all())
        logger.info(f"[ConversationRepository] search_conversations keyword={keyword!r} provider={provider!r} → {len(convs)} result(s)")
        return convs
        
    async def rename_conversation(self, conversation_id: str, new_title: str) -> Optional[Conversation]:
        conv = await self.get_conversation(conversation_id)
        if conv:
            conv.title = new_title
            await self.session.commit()
            return await self.get_conversation(conversation_id)
        return None
        
    async def archive_conversation(self, conversation_id: str, archive_status: bool = True) -> Optional[Conversation]:
        conv = await self.get_conversation(conversation_id)
        if conv:
            conv.is_archived = archive_status
            await self.session.commit()
            return await self.get_conversation(conversation_id)
        return None
        
    async def pin_conversation(self, conversation_id: str, pin_status: bool = True) -> Optional[Conversation]:
        conv = await self.get_conversation(conversation_id)
        if conv:
            conv.is_pinned = pin_status
            await self.session.commit()
            return await self.get_conversation(conversation_id)
        return None
        
    async def get_conversation_by_session(self, session_id: str) -> Optional[Conversation]:
        result = await self.session.execute(
            select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.session_id == session_id).order_by(Conversation.updated_at.desc())
        )
        return result.scalars().first()

    async def add_message(self, conversation_id: str, role: str, content: str, 
                          token_count: Optional[int] = None, provider: Optional[str] = None,
                          message_metadata: Optional[dict] = None,
                          model_name: Optional[str] = None,
                          prompt_tokens: Optional[int] = None,
                          completion_tokens: Optional[int] = None,
                          total_tokens: Optional[int] = None,
                          latency_ms: Optional[int] = None,
                          processing_time: Optional[int] = None,
                          temperature: Optional[float] = None,
                          response_type: Optional[str] = None,
                          language: Optional[str] = None,
                          history_used: Optional[bool] = False,
                          cached: Optional[bool] = False,
                          confidence: Optional[float] = None) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
            provider=provider,
            message_metadata=message_metadata,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            processing_time=processing_time,
            temperature=temperature,
            response_type=response_type,
            language=language,
            history_used=history_used,
            cached=cached,
            confidence=confidence
        )
        self.session.add(message)
        
        # Touch conversation updated_at and update denormalized enterprise metrics
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            # Append message to memory relationship to preserve state and avoid deletes
            if message not in conversation.messages:
                conversation.messages.append(message)
                
            # Updating a field triggers onupdate
            conversation.is_archived = False
            conversation.last_message_at = message.timestamp
            
            if provider:
                conversation.provider = provider
            if message_metadata and "model_used" in message_metadata:
                conversation.model_name = message_metadata["model_used"]
            
        await self.session.commit()
        await self.session.refresh(message)
        logger.info(f"[ConversationRepository] Saved message id={message.id} role={role} conversation_id={conversation_id} — DB commit successful")
        return message
        
    async def update_summary(self, conversation_id: str, summary: str):
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.summary = summary
            await self.session.commit()

    async def delete_conversation(self, conversation_id: str):
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            await self.session.delete(conversation)
            await self.session.commit()

    async def get_message(self, message_id: str) -> Optional[Message]:
        result = await self.session.execute(select(Message).where(Message.id == message_id))
        return result.scalars().first()

    async def update_message(self, message_id: str, new_content: str) -> Optional[Message]:
        message = await self.get_message(message_id)
        if message:
            message.content = new_content
            # Touch conversation
            conv = await self.get_conversation(message.conversation_id)
            if conv:
                conv.last_message_at = datetime.utcnow()
            await self.session.commit()
            logger.info(f"[ConversationRepository] Updated message id={message.id}")
            return message
        return None

    async def delete_message(self, message_id: str) -> bool:
        message = await self.get_message(message_id)
        if message:
            conv_id = message.conversation_id
            await self.session.delete(message)
            # Touch conversation
            conv = await self.get_conversation(conv_id)
            if conv:
                conv.last_message_at = datetime.utcnow()
            await self.session.commit()
            logger.info(f"[ConversationRepository] Deleted message id={message_id}")
            return True
        return False
