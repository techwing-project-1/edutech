from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from app.domain.schemas.general_ai import GeneralAIRequest, GeneralAIResponse, ConversationUpdate, ConversationDetail, MessageUpdate
from app.services.general_ai.manager import GeneralAIManager
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.conversation_repository import ConversationRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.models.conversation import Message
from app.core.logger import logger
from typing import List, Optional

router = APIRouter()

@router.post("/chat", response_model=GeneralAIResponse)
async def general_chat(request: GeneralAIRequest):
    """
    Execute a General AI Chat query.
    Takes a user question and conversation history, compiles templates via the Prompt Builder, 
    and streams the prompt to Gemini (or fallback providers).
    This endpoint supports DB persistence and context management.
    """
    if request.stream:
        from app.services.general_ai.service import GeneralAIService
        service = GeneralAIService()
        return StreamingResponse(service.execute_chat_stream(request), media_type="text/event-stream")
    
    return await GeneralAIManager.chat(request)

@router.get("/conversations/search", response_model=List[ConversationDetail])
async def search_conversations(
    keyword: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Search conversations by keyword or provider."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    logger.info(f"[Route] GET /conversations/search keyword={keyword!r} provider={provider!r} limit={limit}")
    repo = ConversationRepository(db)
    convs = await repo.search_conversations(keyword=keyword, provider=provider, limit=limit, offset=offset)
    logger.info(f"[Route] Search returned {len(convs)} conversation(s)")
    return convs

@router.get("/conversations", response_model=List[ConversationDetail])
async def list_conversations(limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    """List recent active conversations."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    repo = ConversationRepository(db)
    convs = await repo.get_recent_conversations(limit=limit)
    return convs

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Get conversation details and messages."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    logger.info(f"[Route] GET /conversations/{conversation_id}")
    repo = ConversationRepository(db)
    conv = await repo.get_conversation(conversation_id)
    if not conv:
        logger.warning(f"[Route] Conversation {conversation_id} not found")
        raise HTTPException(status_code=404, detail="Conversation not found")
    logger.info(f"[Route] Conversation retrieved id={conv.id} messages={len(conv.messages)}")
    return conv

@router.patch("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str, 
    update_data: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update conversation metadata (rename, pin, archive)."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    repo = ConversationRepository(db)
    conv = await repo.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    if update_data.title is not None:
        await repo.rename_conversation(conversation_id, update_data.title)
    if update_data.is_pinned is not None:
        await repo.pin_conversation(conversation_id, update_data.is_pinned)
    if update_data.is_archived is not None:
        await repo.archive_conversation(conversation_id, update_data.is_archived)
            
    return {"status": "success", "message": "Conversation updated successfully"}

@router.post("/conversations/{conversation_id}/archive")
async def archive_conversation_endpoint(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Archive a conversation."""
    repo = ConversationRepository(db)
    if not await repo.get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    await repo.archive_conversation(conversation_id, True)
    return {"status": "success"}

@router.post("/conversations/{conversation_id}/restore")
async def restore_conversation_endpoint(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Restore an archived conversation."""
    repo = ConversationRepository(db)
    if not await repo.get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    await repo.archive_conversation(conversation_id, False)
    return {"status": "success"}

@router.post("/conversations/{conversation_id}/pin")
async def pin_conversation_endpoint(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Pin a conversation."""
    repo = ConversationRepository(db)
    if not await repo.get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    await repo.pin_conversation(conversation_id, True)
    return {"status": "success"}

@router.post("/conversations/{conversation_id}/unpin")
async def unpin_conversation_endpoint(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Unpin a conversation."""
    repo = ConversationRepository(db)
    if not await repo.get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    await repo.pin_conversation(conversation_id, False)
    return {"status": "success"}

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Permanently delete a conversation."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    repo = ConversationRepository(db)
    conv = await repo.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    await repo.delete_conversation(conversation_id)
    return {"status": "success", "message": "Conversation deleted successfully"}

@router.put("/messages/{message_id}")
async def update_message(message_id: str, update_data: MessageUpdate, db: AsyncSession = Depends(get_db)):
    """Edit an existing message."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    repo = ConversationRepository(db)
    msg = await repo.update_message(message_id, update_data.content)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "success"}

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a specific message."""
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    repo = ConversationRepository(db)
    success = await repo.delete_message(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "success"}
