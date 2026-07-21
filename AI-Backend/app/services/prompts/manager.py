from typing import Dict, Any
from app.services.prompts.builder import PromptBuilder
from app.domain.schemas.llm import LLMRequest
from app.core.logger import logger

class PromptManager:
    """
    High-level facade for creating LLM-ready requests.
    This acts as the bridge between the Prompt Engineering Layer and the LLM Provider Layer.
    It prepares prompts but never executes LLM calls.
    """
    
    @staticmethod
    def create_llm_request(
        system_template_name: str,
        user_template_name: str,
        system_kwargs: Dict[str, Any],
        user_kwargs: Dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        provider_name: str = None,
        model_name: str = None
    ) -> LLMRequest:
        """
        Constructs a completely decoupled LLMRequest object by building system and user prompts independently.
        """
        logger.info(f"Creating LLMRequest. System: {system_template_name}, User: {user_template_name}")
        
        try:
            system_prompt = PromptBuilder.build(system_template_name, **system_kwargs)
        except Exception as e:
            logger.warning(f"Failed to build system template '{system_template_name}': {e}. Falling back to 'general_ai_system_v1'.")
            system_prompt = PromptBuilder.build("general_ai_system_v1", **system_kwargs)
            
        try:
            user_prompt = PromptBuilder.build(user_template_name, **user_kwargs)
        except Exception as e:
            logger.warning(f"Failed to build user template '{user_template_name}': {e}. Falling back to 'general_ai_user_v1'.")
            user_prompt = PromptBuilder.build("general_ai_user_v1", **user_kwargs)
        
        return LLMRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            provider_name=provider_name,
            model_name=model_name
        )
