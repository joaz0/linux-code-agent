# app/config.py
import os
from typing import Dict, List, Optional
from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    BEDROCK = "bedrock"
    OPENAI = "openai"
    GEMINI = "gemini"


class TaskComplexity(str, Enum):
    SIMPLE = "simple"    # Tarefas rápidas
    MEDIUM = "medium"    # Edições moderadas
    COMPLEX = "complex"  # Refatoração, arquitetura, debug profundo


class Settings(BaseSettings):
    # ============================================
    # API KEYS
    # ============================================
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field("us-east-1", env="AWS_DEFAULT_REGION")
    
    # ============================================
    # MODEL CONFIGURATION (SOTA - State of the Art 2025/2026)
    # ============================================
    default_llm_provider: LLMProvider = Field(LLMProvider.ANTHROPIC, env="DEFAULT_LLM_PROVIDER")
    
    # Anthropic: New Claude 3.5 Sonnet (Versão out/2024)
    anthropic_model: str = Field("claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    
    # OpenRouter: DeepSeek R1 (Versão Standard/Paga - Mais estável e "Best Model")
    # A versão :free (deepseek/deepseek-r1:free) está instável/offline (Erro 404).
    # Usando a versão oficial que é muito barata ($0.55/M inputs) e SOTA.
    openrouter_model: str = Field("deepseek/deepseek-r1", env="OPENROUTER_MODEL")
    
    # Bedrock: ID específico da versão v2 do Sonnet 3.5
    bedrock_model_id: str = Field(
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0", 
        env="BEDROCK_MODEL_ID"
    )
    
    # OpenAI: GPT-4o
    openai_model: str = Field("gpt-4o", env="OPENAI_MODEL")

    # Gemini: 1.5 Pro
    gemini_model: str = Field("gemini-1.5-pro-latest", env="GEMINI_MODEL")
    
    # ============================================
    # SYSTEM CONFIGURATION
    # ============================================
    llm_provider: Optional[LLMProvider] = Field(None, env="LLM_PROVIDER")
    llm_model: Optional[str] = Field(None, env="LLM_MODEL")
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    anthropic_base_url: str = Field("https://api.anthropic.com/v1", env="ANTHROPIC_BASE_URL")
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    
    # Timeout aumentado para 180s (Modelos Reasoning como R1 precisam de tempo para "pensar")
    llm_timeout: int = Field(180, env="LLM_TIMEOUT")
    llm_max_retries: int = Field(3, env="LLM_MAX_RETRIES")
    enable_cache: bool = Field(True, env="ENABLE_CACHE")
    cache_ttl: int = Field(86400, env="CACHE_TTL")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # ============================================
    # BUDGET LIMITS (USD)
    # ============================================
    anthropic_monthly_limit: float = Field(50.0, env="ANTHROPIC_MONTHLY_LIMIT")
    openrouter_monthly_limit: float = Field(10.0, env="OPENROUTER_MONTHLY_LIMIT")
    bedrock_monthly_limit: float = Field(100.0, env="BEDROCK_MONTHLY_LIMIT")
    
    # ============================================
    # PROVIDER SELECTION STRATEGY
    # ============================================
    provider_preference: Dict[TaskComplexity, List[LLMProvider]] = {
        # Simple
        TaskComplexity.SIMPLE: [LLMProvider.GEMINI, LLMProvider.OPENAI, LLMProvider.ANTHROPIC],
        
        # Medium
        TaskComplexity.MEDIUM: [LLMProvider.ANTHROPIC, LLMProvider.OPENROUTER, LLMProvider.GEMINI],
        
        # Complex: DeepSeek R1 (OpenRouter) entra como opção de raciocínio profundo
        TaskComplexity.COMPLEX: [LLMProvider.ANTHROPIC, LLMProvider.OPENROUTER, LLMProvider.OPENAI, LLMProvider.GEMINI]
    }
    
    # Custos Estimados (USD por 1K input tokens)
    cost_per_1k_input: Dict[LLMProvider, float] = {
        LLMProvider.ANTHROPIC: 0.003,      # Claude 3.5 Sonnet
        LLMProvider.OPENROUTER: 0.00055,   # DeepSeek R1 (~$0.55/1M tokens - muito barato)
        LLMProvider.BEDROCK: 0.003,        # Via AWS
        LLMProvider.OPENAI: 0.0025,        # GPT-4o
        LLMProvider.GEMINI: 0.00125        # Gemini 1.5 Pro
    }
    
    # ============================================
    # VALIDATORS & PROPERTIES
    # ============================================
    @validator("default_llm_provider", pre=True)
    def validate_default_provider(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [p.value for p in LLMProvider]:
                raise ValueError(f"Provider inválido: {v}. Use: {[p.value for p in LLMProvider]}")
        return v
    
    @property
    def available_providers(self) -> List[LLMProvider]:
        """Retorna lista de providers disponíveis baseado nas keys configuradas."""
        providers = []
        if self.anthropic_api_key: providers.append(LLMProvider.ANTHROPIC)
        if self.openrouter_api_key: providers.append(LLMProvider.OPENROUTER)
        if self.aws_access_key_id and self.aws_secret_access_key: providers.append(LLMProvider.BEDROCK)
        if self.openai_api_key: providers.append(LLMProvider.OPENAI)
        if self.gemini_api_key: providers.append(LLMProvider.GEMINI)
        return providers
    
    @property
    def is_multi_provider_enabled(self) -> bool:
        return len(self.available_providers) > 1

    def resolve_model_for(self, provider: LLMProvider) -> str:
        """
        Retorna o modelo a ser utilizado para um determinado provedor.

        Esta função considera a configuração global `llm_model` como uma
        sobreposição: se definida no ambiente (.env), esse valor será
        utilizado independentemente do provedor selecionado. Caso contrário,
        cada provedor utiliza seu modelo específico configurado em
        `config.py`.

        Args:
            provider: O provedor de linguagem para o qual o modelo deve ser resolvido.

        Returns:
            O nome do modelo a ser utilizado.

        Raises:
            ValueError: Se for solicitado um provedor desconhecido.
        """
        # Se um modelo global estiver definido, utiliza-o para todos os provedores
        if self.llm_model:
            return self.llm_model

        # Caso contrário, resolve por provedor
        if provider == LLMProvider.ANTHROPIC:
            return self.anthropic_model
        if provider == LLMProvider.OPENROUTER:
            return self.openrouter_model
        if provider == LLMProvider.BEDROCK:
            return self.bedrock_model_id
        if provider == LLMProvider.OPENAI:
            return self.openai_model
        if provider == LLMProvider.GEMINI:
            return self.gemini_model

        # Se o provedor não é reconhecido, gera uma exceção
        raise ValueError(f"Provider não suportado: {provider}")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Instância global das configurações
settings = Settings()