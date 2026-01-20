# app/core/llm/multi_provider.py
import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum

try:
    import nest_asyncio
except ImportError:
    nest_asyncio = None

# Importa tenacity para retries resilientes
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Imports do projeto
from app.config import settings, LLMProvider, TaskComplexity
from app.core.llm.clients.base_client import BaseLLMClient
from app.core.llm.clients.anthropic_client import AnthropicClient
from app.core.llm.clients.bedrock_client import BedrockClient
from app.core.llm.clients.gemini_client import GeminiClient
from app.core.llm.clients.openai_client import OpenAIClient

# Imports opcionais de infra (para não quebrar se faltar dependência)
try:
    from app.core.llm.cache_system import cache_system
except ImportError:
    cache_system = None

try:
    from app.core.llm.complexity_estimator import complexity_estimator
except ImportError:
    complexity_estimator = None

try:
    from app.core.llm.metrics_logger import metrics_logger
except ImportError:
    metrics_logger = None

logger = logging.getLogger(__name__)

# Aplica patch para permitir loops aninhados (útil se chamado de dentro de uma rota async)
if nest_asyncio is not None:
    nest_asyncio.apply()

class MultiProviderLLM:
    """
    Sistema Central de Inteligência (SOTA 2026).
    Gerencia múltiplos modelos, roteamento inteligente, fallback e custos.
    """
    
    def __init__(self, use_aws_toolkit: bool = True):
        self.logger = logging.getLogger(__name__)
        self.use_aws_toolkit = use_aws_toolkit
        self.clients: Dict[LLMProvider, BaseLLMClient] = {}
        
        # 1. Inicializa Clientes
        self._initialize_clients()
        
        self.available_providers = list(self.clients.keys())
        
        # 2. Validação Inicial
        if not self.available_providers:
            self.logger.warning("⚠️ Nenhum provedor LLM configurado! O agente não poderá responder.")
        else:
            self.logger.info(f"✅ Provedores Ativos: {[p.value for p in self.available_providers]}")

    def _initialize_clients(self):
        """Inicializa conexões com APIs baseadas no .env"""
        try:
            # Anthropic (Claude 3.5 Sonnet)
            if settings.anthropic_api_key:
                try:
                    self.clients[LLMProvider.ANTHROPIC] = AnthropicClient()
                except Exception as e:
                    self.logger.error(f"Erro Anthropic: {e}")

            # OpenRouter (DeepSeek V3 / Llama 3)
            if settings.openrouter_api_key:
                try:
                    # Fix: Truncate model list to max 3 items (OpenRouter limit)
                    or_model = getattr(settings, "openrouter_model", None) or "deepseek/deepseek-r1:free"
                    if isinstance(or_model, str) and "," in or_model:
                        parts = [p.strip() for p in or_model.split(",")]
                        if len(parts) > 3:
                            or_model = ",".join(parts[:3])
                            self.logger.warning(f"⚠️ OpenRouter model list truncated: {or_model}")
                    
                    if isinstance(or_model, str) and or_model.startswith("@preset"):
                        self.logger.warning(f"⚠️ Usando preset OpenRouter: {or_model}. Isso pode causar erro 400 se contiver >3 modelos.")

                    self.clients[LLMProvider.OPENROUTER] = OpenAIClient(
                        api_key=settings.openrouter_api_key,
                        base_url="https://openrouter.ai/api/v1",
                        model=or_model,
                        provider=LLMProvider.OPENROUTER.value,
                        extra_headers={
                            "HTTP-Referer": "https://agent-auto.local",
                            "X-Title": "Agent Auto"
                        }
                    )
                    self.logger.info(f"✅ OpenRouter conectado. Modelo: {or_model}")
                except Exception as e:
                    self.logger.error(f"Erro OpenRouter: {e}")
            else:
                self.logger.debug("OpenRouter não configurado (OPENROUTER_API_KEY ausente)")

            # Gemini (Google 3.0 Pro)
            if settings.gemini_api_key:
                try:
                    self.clients[LLMProvider.GEMINI] = GeminiClient()
                except Exception as e:
                    self.logger.error(f"Erro Gemini: {e}")

            # OpenAI (GPT-4.5 Turbo)
            if settings.openai_api_key:
                try:
                    self.clients[LLMProvider.OPENAI] = OpenAIClient()
                    self.logger.info("✅ OpenAI client inicializado")
                except Exception as e:
                    self.logger.error(f"Erro OpenAI: {e}")

            # AWS Bedrock (Zero-Config)
            # Tenta se houver chaves explícitas OU se o toolkit estiver ativado
            should_try_aws = (
                self.use_aws_toolkit or 
                (settings.aws_access_key_id and settings.aws_secret_access_key)
            )
            
            if should_try_aws:
                try:
                    import boto3
                    # Teste rápido de sessão para não crashar na inicialização do cliente
                    boto3.Session() 
                    self.clients[LLMProvider.BEDROCK] = BedrockClient()
                    self.logger.info("✅ AWS Bedrock conectado (Zero-Config).")
                except Exception as e:
                    self.logger.debug(f"AWS Bedrock indisponível: {e}")

        except Exception as e:
            self.logger.critical(f"Falha catastrófica ao iniciar LLMs: {e}")

    # =========================================================================
    # MÉTODOS PÚBLICOS DE GERAÇÃO
    # =========================================================================

    def generate_text(
        self, 
        prompt: str, 
        complexity: TaskComplexity = TaskComplexity.MEDIUM,
        provider: Optional[LLMProvider] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Método simplificado e síncrono para geração de texto.
        Ideal para uso no Planner ou scripts simples.
        """
        # Executa a lógica completa de fallback em um loop de eventos
        try:
            response, _ = asyncio.run(self.call_with_fallback(
                prompt=prompt,
                system_prompt=system_prompt,
                complexity=complexity,
                force_provider=provider
            ))
            return response
        except RuntimeError:
            # Se já estivermos num loop (ex: FastAPI), usa o loop existente
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Isso é perigoso em prod, mas nest_asyncio resolveu lá em cima
                response, _ = loop.run_until_complete(self.call_with_fallback(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    complexity=complexity,
                    force_provider=provider
                ))
                return response
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
        Chama LLM com sistema robusto de Fallback (Cascata de Erros).
        Se o modelo principal falhar, tenta o próximo da lista.
        """
        # 1. Determina a Complexidade
        if complexity is None:
            # Tenta estimar se o módulo estiver disponível, senão usa MEDIUM
            complexity = complexity_estimator.estimate(prompt) if complexity_estimator else TaskComplexity.MEDIUM

        # 2. Verifica Cache Semântico
        if settings.enable_cache and cache_system:
            cached = cache_system.get_semantic(prompt)
            if cached:
                self.logger.info("⚡ Cache Hit (Semântico)")
                return cached, {"cached": True, "provider": "cache"}

        # 3. Define a Ordem de Tentativa
        if force_provider:
            providers_to_try = [force_provider]
        else:
            providers_to_try = self._get_fallback_chain(complexity)

        last_error = None
        
        # 4. Loop de Tentativas (Fallback Chain)
        for i, provider in enumerate(providers_to_try):
            # Pula se o cliente não foi inicializado
            if provider not in self.clients:
                continue
            
            try:
                self.logger.info(f"🤖 Tentando: {provider.value} (Tentativa {i+1})")
                
                # Chama o método com retry interno
                response, metrics = await self.call_with_provider(
                    provider=provider,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
                
                # Sucesso! Salva no cache
                if settings.enable_cache and cache_system:
                    try:
                        cache_system.set(
                            prompt=prompt,
                            provider=provider.value,
                            model=self.clients[provider].model,
                            value=response
                        )
                    except Exception as e:
                        self.logger.warning(f"Erro ao salvar cache: {e}")

                # Adiciona meta-info sobre o fallback
                if i > 0:
                    metrics["fallback_occurred"] = True
                    metrics["fallback_depth"] = i
                
                return response, metrics

            except Exception as e:
                last_error = e
                # Check for 402 (Insufficient Credits)
                if "402" in str(e) and provider == LLMProvider.OPENROUTER:
                     self.logger.error("💰 Sem créditos no OpenRouter. Mude para um modelo free (ex: deepseek/deepseek-r1:free) no .env")
                
                self.logger.warning(f"❌ Falha no provedor {provider.value}: {e}")
                
                # Backoff simples antes de tentar o próximo
                if i < len(providers_to_try) - 1:
                    await asyncio.sleep(0.5 * (i + 1))

        # 5. Falha Total
        error_msg = f"Todas as tentativas falharam. Último erro: {last_error}"
        self.logger.error(error_msg)
        
        # Loga a falha se o logger estiver ativo
        if metrics_logger:
            metrics_logger.log_total_failure(
                providers_tried=[p.value for p in providers_to_try],
                last_error=str(last_error),
                prompt_length=len(prompt)
            )
            
        raise Exception(error_msg)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, IOError)),
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
        Executa a chamada a um único provedor com política de Retry automática.
        """
        start_time = time.time()
        client = self.clients[provider]
        
        try:
            # Chama o cliente específico (Anthropic, Gemini, etc.)
            response = await client.call(prompt, system_prompt, **kwargs)
            
            elapsed = time.time() - start_time
            metrics = client.get_metrics()
            
            call_metrics = {
                "provider": provider.value,
                "model": client.model,
                "latency_ms": round(elapsed * 1000, 2),
                "success": True
            }
            
            # Log de sucesso
            if metrics_logger:
                metrics_logger.log_call(
                    provider=provider,
                    prompt=prompt,
                    response=response,
                    metrics=call_metrics
                )
            
            return response, {**metrics, **call_metrics}

        except Exception as e:
            # Apenas loga; o decorator @retry vai tentar novamente ou o loop de fallback vai pegar
            elapsed = time.time() - start_time
            if metrics_logger:
                metrics_logger.log_error(provider=provider, prompt=prompt, error=str(e), response_time=elapsed)
            raise

    # =========================================================================
    # UTILITÁRIOS
    # =========================================================================

    def _get_fallback_chain(self, complexity: TaskComplexity) -> List[LLMProvider]:
        """Define a ordem de provedores baseada na complexidade da tarefa."""
        # Pega a preferência do config.py (Ex: Complex -> [Anthropic, OpenAI])
        preferred = settings.provider_preference.get(complexity, [])
        
        # Filtra apenas os que estão realmente ativos/inicializados
        active_chain = [p for p in preferred if p in self.clients]
        
        # Se a cadeia preferida estiver vazia, usa qualquer um disponível como último recurso
        if not active_chain:
            active_chain = list(self.clients.keys())
            
        return active_chain

    def get_metrics(self) -> Dict[str, Any]:
        """Agrega métricas de todos os clientes ativos."""
        metrics = {}
        for prov, client in self.clients.items():
            metrics[prov.value] = client.get_metrics()
        return metrics

# Singleton Global
multi_provider = MultiProviderLLM()
