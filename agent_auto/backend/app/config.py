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
    # MODEL CONFIGURATION (SOTA - State of the Art 2025)
    # ============================================
    default_llm_provider: LLMProvider = Field(LLMProvider.ANTHROPIC, env="DEFAULT_LLM_PROVIDER")
    
    # Anthropic: New Claude 3.5 Sonnet (Versão out/2024 - Melhor que Opus 3.0 para código)
    anthropic_model: str = Field("claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    
    # OpenRouter: Mapeando para o New Sonnet
    openrouter_model: str = Field("anthropic/claude-3-5-sonnet", env="OPENROUTER_MODEL")
    
    # Bedrock: ID específico da versão v2 do Sonnet 3.5
    bedrock_model_id: str = Field(
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0", 
        env="BEDROCK_MODEL_ID"
    )
    
    # OpenAI: GPT-4o (O mais capaz atualmente)
    openai_model: str = Field("gpt-4o", env="OPENAI_MODEL")

    # Gemini: 1.5 Pro (Melhor raciocínio e contexto do Google)
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
    
    # Timeouts aumentados para modelos complexos
    llm_timeout: int = Field(60, env="LLM_TIMEOUT")
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
        # Simple: Gemini Flash/Pro é rápido e eficiente
        TaskComplexity.SIMPLE: [LLMProvider.GEMINI, LLMProvider.OPENAI, LLMProvider.ANTHROPIC],
        
        # Medium: Claude 3.5 Sonnet é o "sweet spot"
        TaskComplexity.MEDIUM: [LLMProvider.ANTHROPIC, LLMProvider.GEMINI, LLMProvider.OPENROUTER],
        
        # Complex: Prioridade total para o Sonnet 3.5 (Melhor raciocínio de código)
        TaskComplexity.COMPLEX: [LLMProvider.ANTHROPIC, LLMProvider.OPENAI, LLMProvider.GEMINI]
    }
    
    # Custos Estimados (USD por 1K input tokens)
    cost_per_1k_input: Dict[LLMProvider, float] = {
        LLMProvider.ANTHROPIC: 0.003,      # Claude 3.5 Sonnet
        LLMProvider.OPENROUTER: 0.003,     # Via OpenRouter
        LLMProvider.BEDROCK: 0.003,        # Via AWS
        LLMProvider.OPENAI: 0.0025,        # GPT-4o
        LLMProvider.GEMINI: 0.00125        # Gemini 1.5 Pro (<128k context)
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Instância global das configurações
settings = Settings()