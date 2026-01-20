# app/core/llm/clients/base_client.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging


class BaseLLMClient(ABC):
    """Interface base para todos os clients LLM."""
    
    def __init__(self, provider: str, model: str, timeout: int = 30, **kwargs):
        self.provider = provider
        self.model = model
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "errors": 0,
            "last_call": None
        }
    
    @abstractmethod
    async def call(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Chama o LLM e retorna a resposta."""
        pass
    
    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estima custo da chamada."""
        pass
    
    def update_metrics(self, prompt_tokens: int, completion_tokens: int):
        """Atualiza métricas após chamada bem-sucedida."""
        self.metrics["total_calls"] += 1
        self.metrics["total_tokens"] += (prompt_tokens + completion_tokens)
        self.metrics["total_cost"] += self.estimate_cost(prompt_tokens, completion_tokens)
        self.metrics["last_call"] = time.time()
    
    def record_error(self):
        """Registra erro nas métricas."""
        self.metrics["errors"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais."""
        return self.metrics.copy()