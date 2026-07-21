from typing import Any
from app.core.logger import logger

class RAGQueryBuilder:
    """
    Centralized utility to generate RAG semantic search queries.
    Shared across Content Generation Strategies and Agent Orchestrator.
    """
    
    @staticmethod
    def build_query(request: Any, query_override: str = None, fallback: str = "Generate a comprehensive summary of the course syllabus.") -> str:
        """
        Builds a semantic search query based on request parameters.
        Priority:
        1. request.topic (direct property)
        2. request.context.get('topic') (if context is a dict)
        3. query_override (explicitly passed)
        4. request.query (direct property)
        5. fallback (generic string)
        """
        # 1. Check direct topic property
        topic = getattr(request, 'topic', None)
        
        # 2. Check topic inside context (for AgentRequests)
        if not topic:
            context_dict = getattr(request, 'context', {})
            if isinstance(context_dict, dict):
                topic = context_dict.get("topic")
                
        if topic and str(topic).strip():
            logger.info(f"RAGQueryBuilder: Selected 'topic' as search query: '{topic}'")
            return str(topic).strip()
            
        # 3. Check explicit query_override
        # Ignore mock generic agent queries if possible
        if query_override and str(query_override).strip() and "Test query for agent" not in str(query_override):
            logger.info(f"RAGQueryBuilder: Selected 'query_override' as search query: '{query_override}'")
            return str(query_override).strip()
            
        # 4. Check direct query property
        query = getattr(request, 'query', None)
        if query and str(query).strip() and "Test query for agent" not in str(query):
            logger.info(f"RAGQueryBuilder: Selected 'query' as search query: '{query}'")
            return str(query).strip()
            
        # 5. Use Fallback
        logger.info(f"RAGQueryBuilder: Selected generic 'fallback' as search query: '{fallback}'")
        return fallback
