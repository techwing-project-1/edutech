from abc import ABC, abstractmethod
from typing import Dict, Type
from app.domain.schemas.content_generation import GenerationMode, ContentGenerationRequest
from app.domain.schemas.llm import LLMRequest
from app.core.exceptions import UnsupportedGenerationModeError

class BaseContentGenerator(ABC):
    """
    Base strategy class for all content generators.
    Specific modes (Summary, Quiz, etc.) will implement this interface.
    """
    
    @abstractmethod
    def build_prompt(self, request: ContentGenerationRequest, context: str) -> LLMRequest:
        """
        Builds the LLMRequest specific to the generation mode.
        Should utilize the PromptBuilder internally.
        """
        pass

class GeneratorRegistry:
    """
    Registry for content generators.
    Allows mapping GenerationMode to specific generator implementations.
    """
    
    _registry: Dict[GenerationMode, Type[BaseContentGenerator]] = {}

    @classmethod
    def register(cls, mode: GenerationMode, generator_class: Type[BaseContentGenerator]) -> None:
        """
        Registers a generator class for a specific mode.
        """
        cls._registry[mode] = generator_class

    @classmethod
    def get_generator_class(cls, mode: GenerationMode) -> Type[BaseContentGenerator]:
        """
        Retrieves the generator class for a given mode.
        """
        if mode not in cls._registry:
            # Fallback to a base implementation or raise an error if not implemented
            raise UnsupportedGenerationModeError(f"No generator registered for mode: {mode}")
        return cls._registry[mode]

from app.services.content_generation.strategies.summary_strategy import SummaryStrategy
from app.services.content_generation.strategies.assessment_strategy import AssessmentStrategy

# Register specific generators
GeneratorRegistry.register(GenerationMode.SUMMARY, SummaryStrategy)
GeneratorRegistry.register(GenerationMode.SHORT_NOTES, SummaryStrategy)
GeneratorRegistry.register(GenerationMode.LONG_NOTES, SummaryStrategy)
GeneratorRegistry.register(GenerationMode.STUDY_NOTES, SummaryStrategy)

GeneratorRegistry.register(GenerationMode.FLASHCARDS, AssessmentStrategy)
GeneratorRegistry.register(GenerationMode.QUIZ, AssessmentStrategy)
GeneratorRegistry.register(GenerationMode.IMPORTANT_QUESTIONS, AssessmentStrategy)
GeneratorRegistry.register(GenerationMode.MCQS, AssessmentStrategy)
