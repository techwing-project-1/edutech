import asyncio
from typing import List
from app.core.logger import logger
from app.infrastructure.repositories.conversation_repository import ConversationRepository
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.domain.schemas.llm import LLMRequest

import tiktoken

class ContextManager:
    """
    Manages the context window for LLM conversations.
    Trims history and generates summaries using the LLM when context overflows.
    """
    
    def __init__(self):
        self.llm_manager = LLMManager()
        # Default tokenizer for general models
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def estimate_tokens(self, text: str) -> int:
        """
        Uses tiktoken to accurately count tokens.
        """
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def trim_history(self, messages: List, max_tokens: int = 4000) -> List:
        """
        Trims the history by dropping oldest messages if they exceed the max_tokens limit.
        """
        if not messages:
            return []
            
        current_tokens = 0
        retained_messages = []
        
        # Traverse backwards, keeping newest messages first
        for msg in reversed(messages):
            msg_tokens = self.estimate_tokens(msg.content)
            if current_tokens + msg_tokens > max_tokens:
                break
            retained_messages.insert(0, msg)
            current_tokens += msg_tokens
            
        if len(retained_messages) < len(messages):
            logger.info(f"ContextManager trimmed {len(messages) - len(retained_messages)} messages.")
            
        return retained_messages

    async def summarize_history(self, conversation_id: str, messages: List):
        """
        Background task to summarize long conversation history.
        """
        try:
            if not messages:
                return
                
            text_to_summarize = "\n".join([f"{m.role}: {m.content}" for m in messages])
            
            prompt = (
                "You are an expert summarizer. Summarize the following conversation history "
                "so that it retains all important facts, context, and user preferences. "
                "Be concise.\n\n"
                f"CONVERSATION:\n{text_to_summarize}"
            )
            
            llm_request = LLMRequest(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            logger.info(f"Generating summary for conversation {conversation_id}...")
            response = await self.llm_manager.generate_response(llm_request)
            
            from app.infrastructure.database.session import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                repo = ConversationRepository(session)
                await repo.update_summary(conversation_id, extract_text(response))
            logger.info(f"Successfully summarized conversation {conversation_id}.")
        except Exception as e:
            logger.error(f"Failed to summarize conversation {conversation_id}: {str(e)}")

    def trigger_summarization(self, conversation_id: str, messages: List):
        """
        Fires and forgets a background summarization task after every 20 messages.
        """
        if len(messages) > 0 and len(messages) % 20 == 0:
            asyncio.create_task(self.summarize_history(conversation_id, messages))

    async def generate_auto_title(self, conversation_id: str, query: str):
        """
        Background task to auto-generate a title based on the first user query.
        """
        try:
            prompt = (
                "You are an expert title generator. Create a short, concise, and descriptive title "
                "(maximum 5 words) for a conversation that starts with this message. "
                "Do not include quotes or punctuation.\n\n"
                f"MESSAGE: {query}"
            )
            llm_request = LLMRequest(prompt=prompt, temperature=0.3, max_tokens=15)
            response = await self.llm_manager.generate_response(llm_request)
            
            title = extract_text(response).strip(' "\'')
            
            from app.infrastructure.database.session import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                repo = ConversationRepository(session)
                await repo.rename_conversation(conversation_id, title)
                logger.info(f"Auto-generated title '{title}' for conversation {conversation_id}.")
        except Exception as e:
            logger.error(f"Failed to auto-generate title for conversation {conversation_id}: {str(e)}")
