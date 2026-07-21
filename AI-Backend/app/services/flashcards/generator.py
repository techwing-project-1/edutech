from app.domain.schemas.content_generation import GenerationMode, ContentGenerationRequest
from app.domain.schemas.llm import LLMRequest
from app.services.content_generation.registry import BaseContentGenerator, GeneratorRegistry

class FlashcardGenerator(BaseContentGenerator):
    """
    Specific generator strategy for Flashcards.
    Builds the prompt demanding strict JSON array output.
    """
    
    def build_prompt(self, request: ContentGenerationRequest, context: str) -> LLMRequest:
        """
        Builds the prompt specific to flashcards.
        Extracts parameters from additional_params.
        """
        flashcard_type = request.additional_params.get("flashcard_type", "QUESTION_ANSWER")
        difficulty = request.additional_params.get("difficulty", "MEDIUM")
        number_of_cards = request.additional_params.get("number_of_cards", 5)
        
        from app.services.prompts.builder import PromptBuilder
        
        system_prompt = PromptBuilder.get_strict_rag_system_prompt(
            role="Flashcard Creator",
            extra_instructions=(
                f"You are generating {number_of_cards} {flashcard_type} flashcards.\n"
                f"Target difficulty: {difficulty}.\n"
                f"Language: {request.language}.\n"
                f"CRITICAL INSTRUCTION: Questions and answers must ONLY reference retrieved content.\n"
                f"CRITICAL: Output format MUST be a strict JSON array of objects. Do NOT include markdown code blocks (like ```json), just the raw JSON array. "
                f"Each object MUST exactly match this schema: "
                f"{{\n"
                f"  \"card_id\": \"uuid-string\",\n"
                f"  \"question\": \"string (front of card)\",\n"
                f"  \"answer\": \"string (back of card)\",\n"
                f"  \"difficulty\": \"string (EASY, MEDIUM, or HARD)\",\n"
                f"  \"topic\": \"string (specific sub-topic)\",\n"
                f"  \"source\": \"string (MUST be retrieved source document reference, never 'General Knowledge')\",\n"
                f"  \"page_number\": number or null\n"
                f"}}"
            )
        )
        
        prompt = (
            f"Topic: {request.topic}\n\n"
            f"Context Information:\n{context}\n\n"
            f"Please generate exactly {number_of_cards} {flashcard_type} flashcards based ONLY on the provided context."
        )
        
        return LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=request.creativity,
            # Adjust max tokens based on requested number of cards (approx 150 tokens per card)
            max_tokens=request.max_tokens if request.max_tokens else number_of_cards * 150
        )

# Register the specific FlashcardGenerator for GenerationMode.FLASHCARDS
GeneratorRegistry.register(GenerationMode.FLASHCARDS, FlashcardGenerator)
