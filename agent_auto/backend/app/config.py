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
    OPENAI = "openai"  # Para compatibilidade


class TaskComplexity(str, Enum):
    SIMPLE = "simple"    # Listar, ler, buscar
    MEDIUM = "medium"    # Editar 1-2 arquivos
    COMPLEX = "complex"  # Refatorar, multi-arquivo, debug


class Settings(BaseSettings):
    # ============================================
    # API KEYS
    # ============================================
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field("us-east-1", env="AWS_DEFAULT_REGION")
    
    # ============================================
    # MODEL CONFIGURATION
    # ============================================
    default_llm_provider: LLMProvider = Field(LLMProvider.ANTHROPIC, env="DEFAULT_LLM_PROVIDER")
    
    # Modelos por provedor
    anthropic_model: str = Field("claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    openrouter_model: str = Field("anthropic/claude-3-5-sonnet", env="OPENROUTER_MODEL")
    bedrock_model_id: str = Field(
        "anthropic.claude-3-5-sonnet-20241022-v2:0", 
        env="BEDROCK_MODEL_ID"
    )
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    
    # ============================================
    # SYSTEM CONFIGURATION
    # ============================================
    llm_timeout: int = Field(30, env="LLM_TIMEOUT")
    llm_max_retries: int = Field(3, env="LLM_MAX_RETRIES")
    enable_cache: bool = Field(True, env="ENABLE_CACHE")
    cache_ttl: int = Field(86400, env="CACHE_TTL")  # 24 horas
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # ============================================
    # BUDGET LIMITS (em dólares)
    # ============================================
    anthropic_monthly_limit: float = Field(50.0, env="ANTHROPIC_MONTHLY_LIMIT")
    openrouter_monthly_limit: float = Field(10.0, env="OPENROUTER_MONTHLY_LIMIT")
    bedrock_monthly_limit: float = Field(100.0, env="BEDROCK_MONTHLY_LIMIT")
    
    # ============================================
    # PROVIDER SELECTION CONFIG
    # ============================================
    # Ordem de preferência por complexidade (custo otimizado)
    provider_preference: Dict[TaskComplexity, List[LLMProvider]] = {
        TaskComplexity.SIMPLE: [LLMProvider.BEDROCK, LLMProvider.OPENROUTER, LLMProvider.ANTHROPIC],
        TaskComplexity.MEDIUM: [LLMProvider.OPENROUTER, LLMProvider.BEDROCK, LLMProvider.ANTHROPIC],
        TaskComplexity.COMPLEX: [LLMProvider.ANTHROPIC, LLMProvider.OPENROUTER, LLMProvider.BEDROCK]
    }
    
    # Custos por 1K tokens (USD)
    cost_per_1k_input: Dict[LLMProvider, float] = {
        LLMProvider.ANTHROPIC: 0.003,      # Claude 3.5 Sonnet
        LLMProvider.OPENROUTER: 0.0024,    # OpenRouter Sonnet
        LLMProvider.BEDROCK: 0.003,        # Bedrock Sonnet
        LLMProvider.OPENAI: 0.0015         # GPT-4o mini
    }
    
    # ============================================
    # VALIDATORS
    # ============================================
    @validator("default_llm_provider", pre=True)
    def validate_default_provider(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v not in [p.value for p in LLMProvider]:
                raise ValueError(f"Provider inválido: {v}. Use: {[p.value for p in LLMProvider]}")
        return v
    
    # ============================================
    # PROPERTIES
    # ============================================
    @property
    def available_providers(self) -> List[LLMProvider]:
        """Retorna lista de providers disponíveis baseado nas keys configuradas."""
        providers = []
        
        if self.anthropic_api_key:
            providers.append(LLMProvider.ANTHROPIC)
        if self.openrouter_api_key:
            providers.append(LLMProvider.OPENROUTER)
        if self.aws_access_key_id and self.aws_secret_access_key:
            providers.append(LLMProvider.BEDROCK)
        if self.openai_api_key:
            providers.append(LLMProvider.OPENAI)
            
        return providers
    
    @property
    def is_multi_provider_enabled(self) -> bool:
        """Verifica se sistema multi-provider está habilitado."""
        return len(self.available_providers) > 1
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global das configurações
settings = Settings()