from app.domain.schemas.content_generation import GenerationMode
from app.services.content_generation.registry import GeneratorRegistry, BaseContentGenerator

class GeneratorFactory:
    """
    Factory class for instantiating the correct Content Generator 
    based on the requested GenerationMode.
    """
    
    @staticmethod
    def create_generator(mode: GenerationMode) -> BaseContentGenerator:
        """
        Creates and returns an instance of the appropriate generator.
        """
        generator_class = GeneratorRegistry.get_generator_class(mode)
        return generator_class()
