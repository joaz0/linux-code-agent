# app/core/llm/clients/anthropic_client.py
import asyncio
from typing import Optional
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import MessageParam
from .base_client import BaseLLMClient
from app.config import settings


class AnthropicClient(BaseLLMClient):
    """Cliente para Anthropic API."""
    
    def __init__(self):
        super().__init__(
            provider="anthropic",
            model=settings.anthropic_model,
            timeout=settings.llm_timeout
        )
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    async def call(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        try:
            messages: list[MessageParam] = [{"role": "user", "content": prompt}]
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=messages,
                system=system_prompt,
                timeout=self.timeout,
                **kwargs
            )
            
            # Estimar tokens (aproximado)
            prompt_tokens = len(prompt.split())  # Simplificado
            completion_tokens = len(response.content[0].text.split())
            
            self.update_metrics(prompt_tokens, completion_tokens)
            return response.content[0].text
            
        except Exception as e:
            self.record_error()
            self.logger.error(f"Anthropic API error: {e}")
            raise
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Custo do Claude 3.5 Sonnet: $0.003/1K input, $0.015/1K output"""
        input_cost = (prompt_tokens / 1000) * 0.003
        output_cost = (completion_tokens / 1000) * 0.015
        return input_cost + output_cost