from typing import Any
from app.services.prompts.registry import PromptRegistry
from app.services.prompts.loader import PromptLoader
from app.services.prompts.validator import PromptValidator
from app.services.prompts.formatter import PromptFormatter
from app.core.logger import logger

class PromptBuilder:
    """
    The orchestrator of the Prompt Layer.
    Coordinates the Registry, Loader, Validator, and Formatter to construct a final prompt string.
    """
    
    @staticmethod
    def build(template_name: str, **kwargs: Any) -> str:
        """Builds a complete, formatted prompt string from a registered template name."""
        logger.debug(f"Building prompt for: {template_name}")
        
        # 1. Fetch schema from Registry
        schema = PromptRegistry.get(template_name)
        
        # 2. Validate injected variables
        PromptValidator.validate_variables(schema, kwargs)
        
        # 3. Load raw string from filesystem
        raw_template = PromptLoader.load_template(schema.template_path)
        
        # 4. Format the core template
        final_prompt = PromptFormatter.format_template(raw_template, **kwargs)
        
        # 5. Modular Block Insertion (Phase 10: Formatting, Safety, History, Provider instructions)
        # Note: If those blocks are provided in kwargs, they are injected into the raw_template.
        # But here we can also append standardized blocks if they aren't explicitly inside the template.
        safety_block = kwargs.get("safety_instructions", "")
        formatting_block = kwargs.get("formatting_instructions", "")
        provider_block = kwargs.get("provider_instructions", "")
        
        if safety_block:
            final_prompt += f"\n\n### SAFETY INSTRUCTIONS ###\n{safety_block}"
            
        if formatting_block:
            final_prompt += f"\n\n### FORMATTING INSTRUCTIONS ###\n{formatting_block}"
            
        if provider_block:
            final_prompt += f"\n\n### PROVIDER INSTRUCTIONS ###\n{provider_block}"
            
        return final_prompt

    @staticmethod
    def get_strict_rag_system_prompt(role: str, extra_instructions: str = "") -> str:
        """
        Generates the standardized True RAG system prompt.
        Forces the LLM to strictly adhere to the retrieved syllabus context.
        """
        base_prompt = (
            f"You are an AI {role}.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. You MUST ONLY use the retrieved syllabus context.\n"
            "2. Do NOT use your general knowledge.\n"
            "3. Do NOT infer missing topics.\n"
            "4. Do NOT generate generic educational content.\n"
            "5. If information is unavailable, explicitly say so.\n"
        )
        if extra_instructions:
            base_prompt += f"{extra_instructions}\n"
        return base_prompt
