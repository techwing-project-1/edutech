import uuid
from typing import List, Type, TypeVar, Any
from pydantic import BaseModel
from app.domain.schemas.content_generation import ContentGenerationRequest
from app.services.content_generation.manager import ContentGenerationManager
from app.utils.json_parser import SafeJsonParser
from app.core.exceptions import LLMReturnedInvalidJSON
from app.core.logger import logger

T = TypeVar('T', bound=BaseModel)

class JsonArrayGeneratorStrategy:
    """
    Unified strategy for generating and safely parsing arrays of JSON objects 
    (e.g., Quizzes, Flashcards) via the Content Generation Engine.
    """
    def __init__(self, engine: ContentGenerationManager):
        self.engine = engine

    async def generate_json_array(
        self, 
        request: ContentGenerationRequest, 
        model_class: Type[T], 
        array_key: str, 
        max_attempts: int = 3,
        id_field: str = None,
        id_prefix: str = "item_",
        fallback_items: List[T] = None
    ) -> tuple[List[T], dict]:
        """
        Executes the content generation request with retries, safely parses the JSON,
        validates each item against the Pydantic `model_class`, and returns the validated list.
        
        Returns a tuple of (validated_items, metadata).
        """
        last_error = None
        last_raw_content = ""
        engine_response = None
        
        for attempt in range(max_attempts):
            try:
                # Update retry-specific params
                if request.additional_params is None:
                    request.additional_params = {}
                request.additional_params["attempt"] = attempt + 1
                request.additional_params["strict_json_mode"] = True

                engine_response = await self.engine.generate_content(request)
                raw_content = engine_response.content.strip()
                last_raw_content = raw_content
                
                provider_used = engine_response.metadata.get("provider_used", "Unknown")
                model_used = engine_response.metadata.get("model_used", "Unknown")
                req_id = engine_response.metadata.get("request_id", "Unknown")
                
                logger.info(f"[{req_id}] Raw JSON Output (Attempt {attempt+1}):\n{raw_content[:200]}...")
                
                parsed_data = SafeJsonParser.safe_parse_llm_json(
                    raw_response=raw_content,
                    provider=provider_used,
                    model=model_used,
                    request_id=req_id
                )
                
                # Handle either `{"key": [...]}` or `[...]`
                if isinstance(parsed_data, dict) and array_key in parsed_data:
                    items_data = parsed_data[array_key]
                else:
                    items_data = parsed_data
                    
                if not isinstance(items_data, list):
                    raise ValueError(f"Parsed JSON does not contain a list of items for key '{array_key}'.")
                
                validated_items = []
                for item in items_data:
                    try:
                        # Auto-inject ID if requested
                        if id_field and isinstance(item, dict) and id_field not in item:
                            item[id_field] = f"{id_prefix}{uuid.uuid4().hex[:8]}"
                            
                        # Validate with Pydantic
                        validated_item = model_class.model_validate(item)
                        validated_items.append(validated_item)
                    except Exception as item_err:
                        logger.warning(f"[{req_id}] Skipping invalid item due to schema error: {str(item_err)}")
                        continue
                        
                if not validated_items:
                    raise ValueError("No valid items could be parsed from the response.")
                    
                logger.info(f"Successfully generated {len(validated_items)} valid items on attempt {attempt+1}")
                
                metadata = {
                    **engine_response.metadata,
                    "success": True,
                    "retry_attempts": attempt
                }
                # Also pass back language if possible, we'll embed it in metadata
                metadata["language"] = engine_response.language
                return validated_items, metadata
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed to parse or validate JSON: {str(e)}")
                if attempt == max_attempts - 1:
                    logger.error(f"Failed to generate valid JSON after {max_attempts} retries. Raw output:\n{last_raw_content}")
                    break
                    
        # Fallback Handling
        if fallback_items is not None:
            logger.warning(f"Using fallback items after exhausting retries.")
            return fallback_items, {
                "success": False,
                "error": "Invalid LLM JSON output",
                "retry_attempts": max_attempts,
                "language": request.language
            }
        else:
            # Re-raise the Invalid JSON error if no fallback provided
            provider = engine_response.metadata.get("provider_used", "Unknown") if engine_response else "Unknown"
            model = engine_response.metadata.get("model_used", "Unknown") if engine_response else "Unknown"
            req_id = engine_response.metadata.get("request_id", "Unknown") if engine_response else "Unknown"
            raise LLMReturnedInvalidJSON(
                message="Failed to generate valid JSON after retries.",
                raw_output=last_raw_content,
                provider=provider,
                model=model,
                request_id=req_id
            )
