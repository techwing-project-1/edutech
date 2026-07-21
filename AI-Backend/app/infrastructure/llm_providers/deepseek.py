import time
import os
import asyncio
from typing import AsyncGenerator
import openai
from app.domain.interfaces.llm_provider import LLMProviderInterface
from app.domain.schemas.llm import LLMRequest, LLMResponse
from app.core.config import settings
from app.core.exceptions import LLMProviderException, RateLimitError
from app.core.logger import logger

class DeepSeekProvider(LLMProviderInterface):
    """
    Real DeepSeek API Provider using OpenAI SDK.
    """
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY is not set. DeepSeek Provider will fail on execution.")
            self.client = None
        else:
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
            
    @property
    def provider_name(self) -> str:
        return "DeepSeek"

    def _build_messages(self, request: LLMRequest) -> list:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        return messages
        
    async def generate(self, request: LLMRequest) -> LLMResponse:
        logger.info(f"Generating via {self.provider_name}...")
        
        if not self.api_key or not self.client:
            raise LLMProviderException(f"{self.provider_name} is missing API configuration.")
            
        start_time = time.time()
        model_name = request.model_name or "deepseek-chat"
        
        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=self._build_messages(request),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=False
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return LLMResponse.model_validate({
                "answer": response.choices[0].message.content,
                "provider_used": self.provider_name,
                "model_name": model_name,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "latency_ms": latency_ms,
                "finish_reason": response.choices[0].finish_reason or "stop",
                "fallback_used": True,
                "cost": 0.0,
                "response_id": response.id
            })
        except openai.RateLimitError as e:
            logger.error(f"DeepSeek Rate Limit Error: {str(e)}")
            raise RateLimitError("DeepSeek Rate Limit Exceeded", provider=self.provider_name)
        except openai.APIError as e:
            logger.error(f"DeepSeek API Error: {str(e)}")
            raise LLMProviderException(f"DeepSeek API Error: {str(e)}")
        except Exception as e:
            logger.error(f"DeepSeek Unexpected Error: {str(e)}")
            raise LLMProviderException(f"Failed to connect to DeepSeek: {str(e)}")
        
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        logger.info(f"Generating stream via {self.provider_name}...")
        
        if not self.api_key or not self.client:
            raise LLMProviderException(f"{self.provider_name} is missing API configuration.")
            
        model_name = request.model_name or "deepseek-chat"
        
        try:
            stream = await self.client.chat.completions.create(
                model=model_name,
                messages=self._build_messages(request),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except openai.RateLimitError as e:
            raise RateLimitError("DeepSeek Rate Limit Exceeded", provider=self.provider_name)
        except Exception as e:
            raise LLMProviderException(f"Failed to stream from DeepSeek: {str(e)}")
        
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        return True
