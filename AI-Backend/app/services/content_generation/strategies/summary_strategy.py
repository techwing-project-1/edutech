from app.domain.schemas.content_generation import ContentGenerationRequest
from app.domain.schemas.llm import LLMRequest
from app.services.content_generation.strategies.base import BaseContentGenerator

class SummaryStrategy(BaseContentGenerator):
    """
    Strategy for generating text-heavy content like Summaries and Notes.
    """
    
    def build_prompt(self, request: ContentGenerationRequest, context: str) -> LLMRequest:
        from app.services.prompts.builder import PromptBuilder
        system_prompt = PromptBuilder.get_strict_rag_system_prompt(
            role="Educational Content Generator",
            extra_instructions=f"Output format MUST be strictly {request.output_format.value}, properly formatted using Markdown where applicable.\n"
        )

        prompt = f"""Topic: {request.topic}
Content Type Required: {request.mode.value}

Context:
---
{context}
---

Please generate the {request.mode.value} based STRICTLY on the above Context. Do not include introductory conversational text (like "Here is the summary"). Start directly with the content.

FORMATTING REQUIREMENTS:
- Use Professional Markdown format.
- Use proper Headings (##, ###).
- Use Bullet points and Tables ONLY if the document supports them.
- Append the required Citation exactly matching the chunk metadata at the end of every relevant section or claim.
"""
        
        return LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=request.creativity, # Will be clamped by orchestrator
            max_tokens=request.max_tokens
        )
