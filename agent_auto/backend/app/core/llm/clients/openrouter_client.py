# app/core/llm/clients/openrouter_client.py
import asyncio
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from app.config import settings, LLMProvider
from .base_client import BaseLLMClient

logger = logging.getLogger(__name__)

class OpenRouterClient(BaseLLMClient):
    """Cliente para OpenRouter API."""
    
    def __init__(self):
        super().__init__(
            provider="openrouter",
            model=settings.openrouter_model,
            timeout=settings.llm_timeout
        )
        
        # Headers REQUIRED pelo OpenRouter
        extra_headers = {
            "HTTP-Referer": "https://github.com/joaz0/agent_autonomo",
            "X-Title": "Agent Autonomo Linux"
        }
        
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers=extra_headers
        )
        
        logger.info(f"OpenRouter Client inicializado com modelo: {self.model}")
    
    async def call(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Executa uma chamada para a API OpenRouter."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Se for um preset, tenta usar. Se falhar, fallback para DeepSeek Chat
            model_to_use = self.model
            
            response = await self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                timeout=self.timeout,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.1)
            )
            
            # Contagem de tokens
            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
            else:
                # Estimativa aproximada
                prompt_tokens = len(prompt.split())
                completion_tokens = len((response.choices[0].message.content or "").split())
            
            self.update_metrics(prompt_tokens, completion_tokens)
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            # Se falhar com preset, tenta com DeepSeek Chat como fallback
            if '@preset' in self.model:
                logger.warning(f"Preset falhou, tentando DeepSeek Chat: {e}")
                try:
                    # Tenta novamente com DeepSeek Chat
                    response = await self.client.chat.completions.create(
                        model="deepseek/deepseek-chat",
                        messages=messages,
                        timeout=self.timeout,
                        max_tokens=kwargs.get("max_tokens", 1000),
                        temperature=kwargs.get("temperature", 0.1)
                    )
                    
                    if response.usage:
                        prompt_tokens = response.usage.prompt_tokens
                        completion_tokens = response.usage.completion_tokens
                    else:
                        prompt_tokens = len(prompt.split())
                        completion_tokens = len((response.choices[0].message.content or "").split())
                    
                    self.update_metrics(prompt_tokens, completion_tokens)
                    return response.choices[0].message.content or ""
                    
                except Exception as e2:
                    self.record_error()
                    logger.error(f"OpenRouter fallback também falhou: {e2}")
                    raise e2
            else:
                self.record_error()
                logger.error(f"OpenRouter API error: {e}")
                raise
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calcula custo baseado na configuração central."""
        base_input_cost = settings.cost_per_1k_input.get(LLMProvider.OPENROUTER, 0.0018)
        input_cost = (prompt_tokens / 1000) * base_input_cost
        output_cost = (completion_tokens / 1000) * (base_input_cost * 2)
        return input_cost + output_cost
