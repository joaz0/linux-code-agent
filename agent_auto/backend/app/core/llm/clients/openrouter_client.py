# app/core/llm/clients/openrouter_client.py
import asyncio
from typing import Optional
from openai import AsyncOpenAI
from .base_client import BaseLLMClient
from app.config import settings


class OpenRouterClient(BaseLLMClient):
    """Cliente para OpenRouter API."""
    
    def __init__(self):
        super().__init__(
            provider="openrouter",
            model=settings.openrouter_model,
            timeout=settings.llm_timeout
        )
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    async def call(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=self.timeout,
                **kwargs
            )
            
            # Estimar tokens
            prompt_tokens = response.usage.prompt_tokens if response.usage else len(prompt.split())
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            
            self.update_metrics(prompt_tokens, completion_tokens)
            return response.choices[0].message.content
            
        except Exception as e:
            self.record_error()
            self.logger.error(f"OpenRouter API error: {e}")
            raise
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Custo via OpenRouter: $0.0024/1K input, $0.012/1K output"""
        input_cost = (prompt_tokens / 1000) * 0.0024
        output_cost = (completion_tokens / 1000) * 0.012
        return input_cost + output_cost