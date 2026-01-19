# app/core/llm/multi_provider.py
import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings, LLMProvider, TaskComplexity
from app.core.llm.clients.anthropic_client import AnthropicClient
from app.core.llm.clients.openrouter_client import OpenRouterClient
from app.core.llm.clients.bedrock_client import BedrockClient
from app.core.llm.cache_system import cache_system
from app.core.llm.complexity_estimator import complexity_estimator
from app.core.llm.metrics_logger import metrics_logger


class MultiProviderLLM:
    """Sistema principal de rotacionamento inteligente entre múltiplos provedores."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clients = self._initialize_clients()
        self.available_providers = list(self.clients.keys())
        
        # Verificar disponibilidade
        if not self.available_providers:
            raise ValueError("Nenhum provedor LLM configurado. Configure pelo menos uma API key.")
        
        self.logger.info(f"Provedores disponíveis: {self.available_providers}")
    
    def _initialize_clients(self) -> Dict[LLMProvider, any]:
        """Inicializa clientes para provedores configurados."""
        clients = {}
        
        if settings.anthropic_api_key:
            clients[LLMProvider.ANTHROPIC] = AnthropicClient()
        
        if settings.openrouter_api_key:
            clients[LLMProvider.OPENROUTER] = OpenRouterClient()
        
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            clients[LLMProvider.BEDROCK] = BedrockClient()
        
        return clients
    
    def select_provider(self, complexity: TaskComplexity) -> LLMProvider:
        """
        Seleciona o melhor provedor baseado na complexidade da tarefa.
        Implementa fallback automático se o preferido não estiver disponível.
        """
        # Ordem de preferência para esta complexidade
        preferred_order = settings.provider_preference.get(
            complexity, 
            [LLMProvider.ANTHROPIC]  # Fallback
        )
        
        # Filtrar apenas provedores disponíveis
        available_order = [
            provider for provider in preferred_order 
            if provider in self.available_providers
        ]
        
        if not available_order:
            # Fallback para qualquer provedor disponível
            available_order = list(self.available_providers)
        
        if not available_order:
            raise ValueError("Nenhum provedor disponível após filtragem.")
        
        selected = available_order[0]
        self.logger.debug(
            f"Selecionado provedor {selected} para tarefa {complexity}. "
            f"Ordem preferida: {available_order}"
        )
        
        return selected
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True
    )
    async def call_with_provider(
        self, 
        provider: LLMProvider,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, Dict]:
        """
        Chama o LLM usando um provedor específico com retry automático.
        Retorna: (resposta, métricas)
        """
        start_time = time.time()
        
        try:
            client = self.clients[provider]
            response = await client.call(prompt, system_prompt, **kwargs)
            
            # Calcular métricas
            elapsed = time.time() - start_time
            metrics = client.get_metrics()
            
            # Adicionar métricas específicas desta chamada
            call_metrics = {
                "provider": provider.value,
                "model": client.model,
                "response_time": elapsed,
                "success": True,
                "retry_count": 0  # Será atualizado pelo decorator @retry
            }
            
            # Registrar no logger de métricas
            metrics_logger.log_call(
                provider=provider,
                prompt=prompt,
                response=response,
                metrics=call_metrics
            )
            
            return response, {**metrics, **call_metrics}
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"Erro no provedor {provider}: {e}")
            
            # Registrar erro
            metrics_logger.log_error(
                provider=provider,
                prompt=prompt,
                error=str(e),
                response_time=elapsed
            )
            
            raise
    
    async def call_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        complexity: Optional[TaskComplexity] = None,
        force_provider: Optional[LLMProvider] = None,
        **kwargs
    ) -> Tuple[str, Dict]:
        """
        Chama LLM com sistema de fallback automático.
        Se um provedor falhar, tenta o próximo na ordem de preferência.
        """
        # Determinar complexidade se não for fornecida
        if complexity is None:
            complexity = complexity_estimator.estimate(prompt)
        
        # Verificar cache primeiro
        if settings.enable_cache:
            cached = cache_system.get_semantic(prompt)
            if cached:
                self.logger.info("Cache semântico hit")
                return cached, {"cached": True, "provider": "cache"}
        
        # Selecionar provedor
        if force_provider:
            providers_to_try = [force_provider]
        else:
            providers_to_try = self._get_fallback_chain(complexity)
        
        last_error = None
        last_metrics = None
        
        for i, provider in enumerate(providers_to_try):
            if provider not in self.clients:
                continue
            
            try:
                self.logger.info(
                    f"Tentando provedor {provider} "
                    f"({i+1}/{len(providers_to_try)})"
                )
                
                response, metrics = await self.call_with_provider(
                    provider=provider,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
                
                # Armazenar em cache
                if settings.enable_cache:
                    cache_system.set(
                        prompt=prompt,
                        provider=provider.value,
                        model=self.clients[provider].model,
                        value=response
                    )
                
                # Adicionar info de fallback se aplicável
                if i > 0:
                    metrics["fallback_used"] = True
                    metrics["fallback_level"] = i
                    metrics["original_provider"] = providers_to_try[0].value
                
                return response, metrics
                
            except Exception as e:
                last_error = e
                last_metrics = {
                    "provider": provider.value,
                    "error": str(e),
                    "attempt": i + 1
                }
                
                self.logger.warning(
                    f"Falha com provedor {provider}: {e}. "
                    f"Tentando próximo..."
                )
                
                # Aguardar antes de tentar próximo (backoff)
                if i < len(providers_to_try) - 1:
                    await asyncio.sleep(1 * (i + 1))
        
        # Todos os provedores falharam
        error_msg = f"Todos os provedores falharam: {last_error}"
        self.logger.error(error_msg)
        
        # Registrar falha total
        metrics_logger.log_total_failure(
            providers_tried=[p.value for p in providers_to_try],
            last_error=str(last_error),
            prompt_length=len(prompt)
        )
        
        raise Exception(error_msg)
    
    def _get_fallback_chain(self, complexity: TaskComplexity) -> List[LLMProvider]:
        """Gera cadeia de fallback para uma complexidade específica."""
        # Ordem de preferência baseada na complexidade
        preferred = settings.provider_preference.get(
            complexity, 
            [LLMProvider.ANTHROPIC]
        )
        
        # Filtrar apenas provedores disponíveis
        available = [p for p in preferred if p in self.available_providers]
        
        # Se nenhum preferido disponível, usar todos disponíveis
        if not available:
            available = list(self.available_providers)
        
        return available
    
    def get_provider_metrics(self) -> Dict[str, Dict]:
        """Retorna métricas de todos os provedores."""
        metrics = {}
        for provider, client in self.clients.items():
            metrics[provider.value] = client.get_metrics()
        return metrics
    
    def get_cost_estimate(self, prompt: str, provider: Optional[LLMProvider] = None) -> Dict:
        """Estima custo para diferentes provedores."""
        # Estimar tokens (simplificado)
        word_count = len(prompt.split())
        estimated_tokens = word_count * 1.3  # Aproximação
        
        estimates = {}
        
        for prov, client in self.clients.items():
            if provider and prov != provider:
                continue
                
            cost = client.estimate_cost(
                prompt_tokens=estimated_tokens,
                completion_tokens=estimated_tokens * 0.5  # Suposição
            )
            
            estimates[prov.value] = {
                "estimated_cost_usd": cost,
                "estimated_tokens": estimated_tokens,
                "model": client.model
            }
        
        return estimates


# Instância global
multi_provider = MultiProviderLLM()
