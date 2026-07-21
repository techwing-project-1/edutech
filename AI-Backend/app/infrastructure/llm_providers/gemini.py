import os
import time
import asyncio
from google import genai
from google.genai import types
from google.genai import errors
from app.domain.interfaces.llm_provider import LLMProviderInterface
from app.domain.schemas.llm import LLMRequest, LLMResponse
from app.core.config import settings
from app.core.exceptions import LLMProviderException
from app.core.logger import logger
from app.services.llm.error_mapper import ErrorMapper

class GeminiProvider(LLMProviderInterface):
    """
    Google Gemini Provider Implementation.
    This acts as the Primary Provider.
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. Gemini Provider will fail on execution.")
            self.client = None
        else:
            # We initialize standard client here. The async handling and timeouts
            # are configured per request through the new genai SDK config.
            self.client = genai.Client(
                api_key=self.api_key,
                http_options={'timeout': settings.LLM_TIMEOUT}
            )
            
    @property
    def provider_name(self) -> str:
        return "Google Gemini"
        
    def _call_gemini(self, model_name: str, prompt: str, temperature: float, max_tokens: int, enforce_json_mode: bool = False):
        """Internal synchronous call without internal retries. Retries are managed by LLMManager."""
        config_args = {
            "temperature": temperature,
            "max_output_tokens": max_tokens
        }
        if enforce_json_mode:
            config_args["response_mime_type"] = "application/json"
            
        return self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**config_args)
        )
        
    async def generate(self, request: LLMRequest) -> LLMResponse:
        logger.info(f"Generating via {self.provider_name}...")
        
        if not self.api_key or not self.client:
            raise LLMProviderException(f"{self.provider_name} is missing API configuration.")
            
        model_name = request.model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        start_time = time.time()
        try:
            prompt = request.prompt
            if request.system_prompt:
                prompt = f"{request.system_prompt}\n\n{request.prompt}"

            config_args = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
                "automatic_function_calling": {"disable": True}
            }
            if request.enforce_json_mode:
                config_args["response_mime_type"] = "application/json"

            # Execute without internal retries using async client.
            response = await self.client.aio.models.generate_content(
                model=model_name, 
                contents=prompt, 
                config=types.GenerateContentConfig(**config_args)
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            try:
                answer_text = response.text
            except ValueError:
                raise LLMProviderException("Gemini response was blocked by safety settings or contained no text.")
            
            if not answer_text or not answer_text.strip():
                raise LLMProviderException("Gemini returned an empty string.")
            
            return LLMResponse.model_validate({
                "answer": answer_text,
                "provider_used": self.provider_name,
                "model_name": model_name,
                "usage": {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                },
                "latency_ms": latency_ms,
                "finish_reason": "stop",
                "fallback_used": False,
            })
        except Exception as e:
            mapped_error = ErrorMapper.map_gemini_error(e)
            raise mapped_error
            
    async def generate_stream(self, request: LLMRequest):
        logger.info(f"Generating stream via {self.provider_name}...")
        
        if not self.api_key or not self.client:
            raise LLMProviderException(f"{self.provider_name} is missing API configuration.")
            
        model_name = request.model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        try:
            prompt = request.prompt
            if request.system_prompt:
                prompt = f"{request.system_prompt}\n\n{request.prompt}"

            response_stream = await self.client.aio.models.generate_content_stream(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=request.temperature,
                    max_output_tokens=request.max_tokens,
                    automatic_function_calling={"disable": True}
                )
            )
            
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
                
        except Exception as e:
            raise ErrorMapper.map_gemini_error(e)

    async def health_check(self) -> bool:
        """Health check for Gemini."""
        return bool(self.api_key)
