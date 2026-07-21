import time
import httpx
import json
import os
import asyncio
from typing import AsyncGenerator
from app.domain.interfaces.llm_provider import LLMProviderInterface
from app.domain.schemas.llm import LLMRequest, LLMResponse
from app.core.config import settings
from app.core.exceptions import LLMProviderException
from app.core.logger import logger
from app.services.llm.error_mapper import ErrorMapper

class OpenRouterProvider(LLMProviderInterface):
    """
    Real OpenRouter API Provider Implementation.
    """
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY is not set. OpenRouter Provider will fail on execution.")
            
    @property
    def provider_name(self) -> str:
        return "OpenRouter"

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "CurriculaMind AI",
            "Content-Type": "application/json"
        }

    def _build_payload(self, request: LLMRequest, stream: bool = False) -> dict:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        payload = {
            "model": request.model_name or "openrouter/auto",
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": stream
        }
        
        if request.enforce_json_mode:
            payload["response_format"] = {"type": "json_object"}
            
        return payload
        
    async def generate(self, request: LLMRequest) -> LLMResponse:
        logger.info(f"Generating via {self.provider_name} using model {request.model_name or 'openrouter/auto'}...")
        
        if not self.api_key:
            raise LLMProviderException(f"{self.provider_name} is missing API configuration.")
            
        start_time = time.time()
        
        try:
            # Enforce 15.0 second strict timeout for all phases
            timeout_config = httpx.Timeout(settings.LLM_TIMEOUT, connect=settings.LLM_TIMEOUT, read=settings.LLM_TIMEOUT, write=settings.LLM_TIMEOUT)
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._build_headers(),
                    json=self._build_payload(request, stream=False)
                )
                
                response.raise_for_status()
                data = response.json()
                
                choices = data.get("choices", [])
                if not choices:
                    raise LLMProviderException("OpenRouter returned no choices in response.")
                    
                answer = choices[0].get("message", {}).get("content", "")
                
                if not answer or not answer.strip():
                    raise LLMProviderException("OpenRouter returned an empty string.")
                    
                usage = data.get("usage", {})
                latency_ms = int((time.time() - start_time) * 1000)
                
                cost = 0.0
                if "x-total-cost" in response.headers:
                    try:
                        cost = float(response.headers["x-total-cost"])
                    except (ValueError, TypeError):
                        pass
                
                return LLMResponse.model_validate({
                    "answer": answer,
                    "provider_used": self.provider_name,
                    "model_name": request.model_name or "openrouter/auto",
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    "cost": cost,
                    "latency_ms": latency_ms,
                    "finish_reason": choices[0].get("finish_reason", "stop"),
                    "fallback_used": False,
                })
        except Exception as e:
            raise ErrorMapper.map_openrouter_error(e)
        
    async def generate_stream(self, request: LLMRequest):
        logger.info(f"Generating stream via {self.provider_name} using model {request.model_name or 'openrouter/auto'}...")
        
        if not self.api_key:
            raise LLMProviderException(f"{self.provider_name} is missing API configuration.")
            
        try:
            timeout_config = httpx.Timeout(settings.LLM_TIMEOUT, connect=settings.LLM_TIMEOUT, read=settings.LLM_TIMEOUT, write=settings.LLM_TIMEOUT)
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._build_headers(),
                    json=self._build_payload(request, stream=True)
                ) as response:
                
                    response.raise_for_status()
                        
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                pass
                            
        except Exception as e:
            raise ErrorMapper.map_openrouter_error(e)
        
    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(f"{self.base_url}/auth/key", headers=self._build_headers())
                return resp.status_code == 200
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning(f"OpenRouter health check request failed: {e}")
                return False
