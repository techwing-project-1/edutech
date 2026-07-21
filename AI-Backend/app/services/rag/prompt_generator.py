from typing import Dict, Any
from app.domain.schemas.llm import LLMRequest
from app.services.prompts.manager import PromptManager
from app.services.prompts.constants import PromptCategory

class PromptContextGenerator:
    """
    Integrates the built context string into the Prompt Engineering Layer.
    """
    
    @staticmethod
    def generate_llm_request(question: str, context_string: str) -> LLMRequest:
        """
        Uses PromptManager to inject the specific {context} and {question} into the template.
        """
        system_kwargs = {"context": context_string}
        user_kwargs = {"question": question}
        
        return PromptManager.create_llm_request(
            system_template_name="course_assistant_system_v1",
            user_template_name="course_assistant_user_v1",
            system_kwargs=system_kwargs,
            user_kwargs=user_kwargs,
            temperature=0.3, # Low temperature for RAG to ensure factual responses
            max_tokens=2048
        )
