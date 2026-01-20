# app/core/llm/clients/openai_client.py

import asyncio
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from app.config import settings, LLMProvider
from app.core.llm.clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)

class OpenAIClient(BaseLLMClient):
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 base_url: Optional[str] = None, 
                 model: Optional[str] = None,
                 provider: str = LLMProvider.OPENAI.value,
                 extra_headers: Optional[Dict[str, str]] = None):
        resolved_model = model or settings.resolve_model_for(LLMProvider.OPENAI)
        resolved_timeout = settings.llm_timeout
        super().__init__(
            provider=provider,
            model=resolved_model,
            timeout=resolved_timeout
        )
        
        # Configuração da API Key com proteção contra vazamento de credenciais
        client_api_key = api_key
        if provider == LLMProvider.OPENAI.value:
            # Para OpenAI: Usa chave passada > settings > env var (padrão da lib)
            client_api_key = client_api_key or settings.openai_api_key
        elif not client_api_key:
            # Para outros (OpenRouter, etc): Se não passar chave, força erro em vez de usar OpenAI Key
            client_api_key = "missing_key"
            logger.warning(f"⚠️  Client {provider} inicializado sem API Key! Chamadas falharão com 401.")

        self.client = AsyncOpenAI(
            api_key=client_api_key,
            base_url=base_url,
            default_headers=extra_headers
        )
        logger.info(f"✅ OpenAI Client inicializado com modelo: {self.model}")

    async def call(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Executa uma chamada para a API OpenAI."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})

            # Chamada assíncrona nativa
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.1),
                max_tokens=kwargs.get("max_tokens", 2000),
                timeout=self.timeout
            )
            
            content = response.choices[0].message.content
            
            # Atualiza métricas
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            self.update_metrics(prompt_tokens, completion_tokens)
            
            return content
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ Erro no {self.provider}: {e}")
            raise

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estima o custo da chamada baseado no número de tokens."""
        # Pega o custo por 1k tokens de input do settings
        cost_per_1k = settings.cost_per_1k_input.get(LLMProvider.OPENAI, 0.0)
        # Calcula custo (simplificado: usa mesmo custo para input e output)
        total_tokens = prompt_tokens + completion_tokens
        cost = (total_tokens / 1000) * cost_per_1k
        return cost

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do cliente."""
        return self.metrics.copy()
