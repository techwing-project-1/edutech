from app.domain.schemas.content_generation import ContentGenerationRequest
from app.domain.schemas.llm import LLMRequest
from app.services.content_generation.strategies.base import BaseContentGenerator

class AssessmentStrategy(BaseContentGenerator):
    """
    Strategy for generating structured assessments like Quizzes, MCQs, and Flashcards.
    Requires strict JSON or structured outputs and hallucination-free distractors.
    """
    
    def build_prompt(self, request: ContentGenerationRequest, context: str) -> LLMRequest:
        strict_mode = request.additional_params.get("strict_json_mode", False) if request.additional_params else False
        strict_instruction = ""
        if strict_mode:
            strict_instruction = "CRITICAL: YOU MUST RETURN ONLY VALID JSON. NO MARKDOWN. NO EXPLANATIONS. NO CODE BLOCKS. ANY TEXT OUTSIDE THE JSON WILL CAUSE A SYSTEM FAILURE."

        from app.services.prompts.builder import PromptBuilder
        
        system_prompt = PromptBuilder.get_strict_rag_system_prompt(
            role="Educational Assessment Generator",
            extra_instructions=(
                f"Output format MUST be strictly valid {request.output_format.value}. If JSON is requested, output ONLY valid JSON without Markdown blocks wrapping it.\n"
                f"{strict_instruction}\n"
                "SPECIAL INSTRUCTION FOR ASSESSMENTS (MCQs, Quizzes):\n"
                "- When generating distractors (incorrect options), ensure they are plausible but CLEARLY INCORRECT based ONLY on the provided context.\n"
                "- DO NOT pull in external domain knowledge to create distractors if the context doesn't support them.\n"
            )
        )

        prompt = f"""Topic: {request.topic}
Content Type Required: {request.mode.value}

Context:
---
{context}
---

Please generate the {request.mode.value} based STRICTLY on the above Context. Make sure the output exactly matches {request.output_format.value} structure. Do not include introductory conversational text (like "Here is the quiz"). Start directly with the content.

FORMATTING REQUIREMENTS:
If {request.mode.value} == FLASHCARDS:
You MUST output EXACTLY a JSON array of objects, with NO surrounding text, where EACH object has EXACTLY these keys:
- "card_id": A unique string ID (e.g., "fc_001")
- "question": The front of the flashcard
- "answer": The back of the flashcard
- "difficulty": "EASY", "MEDIUM", or "HARD"
- "topic": The specific topic
- "source": The Citation string exactly matching the provided Source block
- "page_number": null (or the integer page number if available)

If {request.mode.value} in [QUIZ, MCQS]:
You MUST output EXACTLY a JSON object with a single key "questions" containing a JSON array of objects, with NO surrounding text, where EACH object has EXACTLY these keys:
- "question": The question text
- "options": An array of exactly 4 strings
- "correct_answer": The exact string matching one of the options
- "explanation": Brief explanation of the answer
- "difficulty": "EASY", "MEDIUM", or "HARD"
- "topic": The specific topic
- "source": The Citation string exactly matching the provided Source block
- "page_number": null (or the integer page number if available)

The Citation must exactly match the source metadata provided in the Context.
"""
        
        return LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=request.creativity, # Will be clamped by orchestrator
            max_tokens=request.max_tokens,
            enforce_json_mode=strict_mode
        )
