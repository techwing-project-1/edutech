from app.domain.schemas.content_generation import GenerationMode, ContentGenerationRequest
from app.domain.schemas.llm import LLMRequest
from app.services.content_generation.registry import BaseContentGenerator, GeneratorRegistry

class StudyNotesGenerator(BaseContentGenerator):
    """
    Specific generator strategy for Study Notes.
    This class builds the prompt for generating structured study notes.
    """
    
    def build_prompt(self, request: ContentGenerationRequest, context: str) -> LLMRequest:
        """
        Builds the prompt specific to study notes.
        Extracts note_type, length, and include_mermaid from additional_params.
        """
        note_type = request.additional_params.get("note_type", "DETAILED")
        length_words = request.additional_params.get("length_words", 500)
        include_mermaid = request.additional_params.get("include_mermaid", False)
        
        from app.services.prompts.builder import PromptBuilder
        
        system_prompt = PromptBuilder.get_strict_rag_system_prompt(
            role="Educational AI Engineer and Study Note Creator",
            extra_instructions=(
                f"You are generating {note_type.replace('_', ' ').title()} Study Notes.\n"
                f"Target length: Approximately {length_words} words.\n"
                f"Language: {request.language}.\n"
                f"CRITICAL INSTRUCTION: Follow document heading hierarchy. Do not reorganize into generic textbook chapters.\n"
                f"Output format MUST be {request.output_format}.\n"
            )
        )

        formatting_rules = (
            "- Use well-structured headings (H1, H2, H3).\n"
            "- Use numbered sections where sequential logic is needed.\n"
            "- Use bullet points for easy readability.\n"
            "- Highlight important concepts using bold or distinct formatting.\n"
            "- Highlight and isolate formulas clearly.\n"
            "- Clearly identify and highlight definitions.\n"
            "- Add a section highlighting important exam points or key takeaways.\n"
            "- Use tables whenever applicable for comparisons or structured data.\n"
        )
        
        if include_mermaid and request.output_format == "MARKDOWN":
            formatting_rules += "- If applicable, include Mermaid diagrams to visually explain concepts.\n"

        prompt = (
            f"Topic/Question: {request.topic}\n\n"
            f"Context Information:\n{context}\n\n"
            f"Please generate comprehensive {note_type.replace('_', ' ').title()} study notes based ONLY on the provided context.\n"
            f"Ensure the following formatting rules are strictly applied:\n"
            f"{formatting_rules}"
        )
        
        return LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=request.creativity,
            max_tokens=request.max_tokens
        )

# Register the specific StudyNotesGenerator for GenerationMode.STUDY_NOTES
GeneratorRegistry.register(GenerationMode.STUDY_NOTES, StudyNotesGenerator)
