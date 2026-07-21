from app.domain.schemas.content_generation import GenerationMode, ContentGenerationRequest
from app.domain.schemas.llm import LLMRequest
from app.services.content_generation.registry import BaseContentGenerator, GeneratorRegistry

class SummaryGenerator(BaseContentGenerator):
    """
    Specific generator strategy for Summaries.
    This class builds the prompt for generating summaries.
    """
    
    def build_prompt(self, request: ContentGenerationRequest, context: str) -> LLMRequest:
        """
        Builds the prompt specific to summaries.
        Extracts summary_type and length from additional_params.
        """
        summary_type = request.additional_params.get("summary_type", "SHORT")
        length_words = request.additional_params.get("length_words", 250)
        
        from app.services.prompts.builder import PromptBuilder
        
        system_prompt = PromptBuilder.get_strict_rag_system_prompt(
            role="Summary Generator",
            extra_instructions=(
                f"You are generating a {summary_type} summary.\n"
                f"Target length: Approximately {length_words} words.\n"
                f"Language: {request.language}.\n"
                f"CRITICAL INSTRUCTION: Every paragraph MUST reference retrieved chunks.\n"
                f"Output format MUST be {request.output_format}."
            )
        )
        
        prompt = (
            f"Topic/Question: {request.topic}\n\n"
            f"Context Information:\n{context}\n\n"
            f"Please generate a comprehensive {summary_type} summary based ONLY on the provided context."
        )
        
        # Note: In a real implementation, you would use PromptBuilder to load 
        # a template from the prompts folder, but we construct it here dynamically
        # to fulfill the specific module logic without duplicating templates.
        
        return LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=request.creativity,
            max_tokens=request.max_tokens
        )

# Register the specific SummaryGenerator for GenerationMode.SUMMARY
GeneratorRegistry.register(GenerationMode.SUMMARY, SummaryGenerator)
