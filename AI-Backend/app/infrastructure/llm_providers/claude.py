import time
import asyncio
from typing import AsyncGenerator
import anthropic
from app.domain.interfaces.llm_provider import LLMProviderInterface
from app.domain.schemas.llm import LLMRequest, LLMResponse
from app.core.config import settings
from app.core.exceptions import LLMProviderException, RateLimitError
from app.core.logger import logger

class ClaudeProvider(LLMProviderInterface):
    """
    Real Anthropic API Provider Implementation.
    """
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY is not set. Claude Provider will fail on execution.")
            self.client = None
        else:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            
    @property
    def provider_name(self) -> str:
        return "Anthropic Claude"

    def _build_messages(self, request: LLMRequest) -> list:
        return [{"role": "user", "content": request.prompt}]
        
    async def generate(self, request: LLMRequest) -> LLMResponse:
        logger.info(f"Generating via {self.provider_name}...")
        
        if not self.api_key or not self.client:
            raise LLMProviderException(f"{self.provider_name} is missing API configuration.")
            
        start_time = time.time()
        model_name = request.model_name or "claude-3-5-sonnet-20240620"
        
        try:
            kwargs = {
                "model": model_name,
                "messages": self._build_messages(request),
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
            }
            if request.system_prompt:
                kwargs["system"] = request.system_prompt
                
            response = await self.client.messages.create(**kwargs)
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return LLMResponse.model_validate({
                "answer": response.content[0].text,
                "provider_used": self.provider_name,
                "model_name": model_name,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "latency_ms": latency_ms,
                "finish_reason": response.stop_reason or "stop",
                "fallback_used": True,
                "cost": 0.0,
                "response_id": response.id
            })
        except anthropic.RateLimitError as e:
            logger.error(f"Claude Rate Limit Error: {str(e)}")
            raise RateLimitError("Anthropic Rate Limit Exceeded")
        except anthropic.APIError as e:
            logger.error(f"Claude API Error: {str(e)}")
            raise LLMProviderException(f"Anthropic API Error: {str(e)}")
        except Exception as e:
            logger.error(f"Claude Unexpected Error: {str(e)}")
            raise LLMProviderException(f"Failed to connect to Anthropic: {str(e)}")
        
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        logger.info(f"Generating stream via {self.provider_name}...")
        
        if not self.api_key or not self.client:
            raise LLMProviderException(f"{self.provider_name} is missing API configuration.")
            
        model_name = request.model_name or "claude-3-5-sonnet-20240620"
        
        try:
            kwargs = {
                "model": model_name,
                "messages": self._build_messages(request),
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
            }
            if request.system_prompt:
                kwargs["system"] = request.system_prompt
                
            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except anthropic.RateLimitError as e:
            raise RateLimitError("Anthropic Rate Limit Exceeded")
        except Exception as e:
            raise LLMProviderException(f"Failed to stream from Anthropic: {str(e)}")
        
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        return True
