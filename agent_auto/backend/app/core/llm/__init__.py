# app/core/llm/__init__.py
"""
Sistema Multi-Provider LLM para Agent Autônomo.

Este módulo fornece:
1. Rotacionamento inteligente entre múltiplos provedores LLM
2. Estimativa de complexidade de tarefas
3. Cache semântico para economia de custos
4. Métricas detalhadas e logging
5. Fallback automático em caso de falhas
"""

from app.core.llm.multi_provider import MultiProviderLLM, multi_provider
from app.core.llm.complexity_estimator import ComplexityEstimator, complexity_estimator
from app.core.llm.cache_system import SemanticCache, cache_system
from app.core.llm.metrics_logger import MetricsLogger, metrics_logger

__all__ = [
    'MultiProviderLLM',
    'multi_provider',
    'ComplexityEstimator', 
    'complexity_estimator',
    'SemanticCache',
    'cache_system',
    'MetricsLogger',
    'metrics_logger'
]