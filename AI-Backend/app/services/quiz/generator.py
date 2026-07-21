from app.domain.schemas.content_generation import GenerationMode, ContentGenerationRequest
from app.domain.schemas.llm import LLMRequest
from app.services.content_generation.registry import BaseContentGenerator, GeneratorRegistry

class QuizGenerator(BaseContentGenerator):
    """
    Specific generator strategy for Quizzes.
    Builds the prompt demanding strict JSON array output for quiz questions.
    """
    
    def build_prompt(self, request: ContentGenerationRequest, context: str) -> LLMRequest:
        """
        Builds the prompt specific to quizzes.
        Extracts parameters from additional_params.
        """
        quiz_type = request.additional_params.get("quiz_type", "MULTIPLE_CHOICE")
        difficulty = request.additional_params.get("difficulty", "MEDIUM")
        number_of_questions = request.additional_params.get("number_of_questions", 10)
        attempt = request.additional_params.get("attempt", 1)
        
        from app.services.prompts.builder import PromptBuilder
        
        extra = (
            f"You are generating exactly {number_of_questions} quiz questions.\n"
            f"Question Type: {quiz_type}.\n"
            f"Target difficulty: {difficulty}.\n"
            f"Language: {request.language}.\n"
            f"CRITICAL INSTRUCTION: Questions must ONLY come from document chunks. No generic {request.topic} questions.\n"
        )
        
        if attempt >= 2:
            extra += "CRITICAL WARNING: Your previous response was invalid. YOU MUST RETURN ONLY RAW JSON.\n"
            
        if attempt >= 3:
            extra += "ULTRA STRICT MODE ENFORCED: DO NOT output any conversational text. DO NOT output markdown. The very first character must be `{` and the last character must be `}`.\n"

        extra += (
            f"CRITICAL: Output format MUST be a strict JSON object containing a 'questions' array. Do NOT include markdown code blocks.\n"
            f"The root must be a JSON object.\n"
            f"Each object in the 'questions' array MUST exactly match this schema:\n"
            f"{{\n"
            f"  \"questions\": [\n"
            f"    {{\n"
            f"  \"question\": \"string (the question text)\",\n"
            f"  \"difficulty\": \"string (EASY, MEDIUM, or HARD)\",\n"
            f"  \"options\": [\"string\", \"string\"] (array of options if applicable, otherwise null),\n"
            f"  \"correct_answer\": \"string (the correct answer or key points)\",\n"
            f"  \"explanation\": \"string (why the answer is correct)\",\n"
            f"  \"topic\": \"string (specific sub-topic)\",\n"
            f"  \"source\": \"string (MUST be retrieved source document reference, never 'General Knowledge')\",\n"
            f"  \"page_number\": number or null\n"
            f"    }}\n"
            f"  ]\n"
            f"}}\n"
            f"Return ONLY JSON. Do NOT return text before or after the JSON."
        )
        
        system_prompt = PromptBuilder.get_strict_rag_system_prompt(
            role="Educational Quiz Creator",
            extra_instructions=extra
        )
        
        prompt = (
            f"Topic: {request.topic}\n\n"
            f"Context Information:\n{context}\n\n"
            f"Please generate exactly {number_of_questions} quiz questions based ONLY on the provided context."
        )
        
        # Adjust max tokens based on requested number of questions
        # Assume roughly 400 tokens per question to prevent truncation
        calculated_tokens = (number_of_questions * 400) + 1000
        max_tokens = request.max_tokens if request.max_tokens and request.max_tokens > calculated_tokens else calculated_tokens

        return LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=request.creativity if attempt == 1 else 0.1, # Lower temperature on retries for strictness
            max_tokens=max_tokens,
            enforce_json_mode=True # Custom flag for Providers
        )

# Register the specific QuizGenerator for GenerationMode.QUIZ
GeneratorRegistry.register(GenerationMode.QUIZ, QuizGenerator)
