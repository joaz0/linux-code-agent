# app/core/llm/metrics_logger.py
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from app.config import LLMProvider


@dataclass
class LLMCallMetrics:
    """Métricas de uma chamada LLM."""
    timestamp: datetime
    provider: str
    model: str
    prompt_length: int
    response_length: int
    response_time: float
    estimated_cost: float
    success: bool
    error_message: Optional[str] = None
    cache_hit: bool = False
    fallback_used: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MetricsLogger:
    """Sistema centralizado de logging de métricas LLM."""
    
    def __init__(self, log_dir: str = "logs/llm_metrics"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Loggers
        self.metrics_logger = logging.getLogger("llm_metrics")
        self.error_logger = logging.getLogger("llm_errors")
        
        # Setup de arquivos de log
        self._setup_logging()
        
        # Estatísticas em tempo real
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "providers": {}
        }
    
    def _setup_logging(self):
        """Configura handlers de logging."""
        # Arquivo de métricas
        metrics_file = self.log_dir / "metrics.jsonl"
        metrics_handler = logging.FileHandler(metrics_file)
        metrics_handler.setFormatter(logging.Formatter('%(message)s'))
        self.metrics_logger.addHandler(metrics_handler)
        self.metrics_logger.setLevel(logging.INFO)
        
        # Arquivo de erros
        error_file = self.log_dir / "errors.log"
        error_handler = logging.FileHandler(error_file)
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.error_logger.addHandler(error_handler)
        self.error_logger.setLevel(logging.ERROR)
    
    def log_call(
        self,
        provider: LLMProvider,
        prompt: str,
        response: str,
        metrics: Dict[str, Any]
    ):
        """Registra uma chamada LLM bem-sucedida."""
        call_metrics = LLMCallMetrics(
            timestamp=datetime.now(),
            provider=provider.value,
            model=metrics.get("model", "unknown"),
            prompt_length=len(prompt),
            response_length=len(response),
            response_time=metrics.get("response_time", 0),
            estimated_cost=metrics.get("estimated_cost", 0),
            success=True,
            cache_hit=metrics.get("cached", False),
            fallback_used=metrics.get("fallback_used", False)
        )
        
        # Log em JSONL
        self.metrics_logger.info(json.dumps(call_metrics.to_dict(), default=str))
        
        # Atualizar estatísticas
        self._update_stats(provider, call_metrics, success=True)
    
    def log_error(
        self,
        provider: LLMProvider,
        prompt: str,
        error: str,
        response_time: float
    ):
        """Registra uma chamada LLM que falhou."""
        call_metrics = LLMCallMetrics(
            timestamp=datetime.now(),
            provider=provider.value,
            model="unknown",
            prompt_length=len(prompt),
            response_length=0,
            response_time=response_time,
            estimated_cost=0,
            success=False,
            error_message=error
        )
        
        # Log de erro
        self.error_logger.error(
            f"Provider {provider.value} failed: {error} "
            f"(prompt: {prompt[:100]}...)"
        )
        
        # Atualizar estatísticas
        self._update_stats(provider, call_metrics, success=False)
    
    def log_total_failure(
        self,
        providers_tried: list,
        last_error: str,
        prompt_length: int
    ):
        """Registra falha total após tentar todos os provedores."""
        self.error_logger.error(
            f"All providers failed: {providers_tried}. "
            f"Last error: {last_error}. "
            f"Prompt length: {prompt_length}"
        )
    
    def _update_stats(self, provider: LLMProvider, metrics: LLMCallMetrics, success: bool):
        """Atualiza estatísticas em tempo real."""
        provider_key = provider.value
        
        if provider_key not in self.stats["providers"]:
            self.stats["providers"][provider_key] = {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "total_cost": 0.0,
                "total_tokens": 0
            }
        
        self.stats["total_calls"] += 1
        
        if success:
            self.stats["successful_calls"] += 1
            self.stats["providers"][provider_key]["successes"] += 1
        else:
            self.stats["failed_calls"] += 1
            self.stats["providers"][provider_key]["failures"] += 1
        
        self.stats["providers"][provider_key]["calls"] += 1
        self.stats["providers"][provider_key]["total_cost"] += metrics.estimated_cost
        
        total_tokens = metrics.prompt_length + metrics.response_length
        self.stats["total_cost"] += metrics.estimated_cost
        self.stats["total_tokens"] += total_tokens
        self.stats["providers"][provider_key]["total_tokens"] += total_tokens
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Retorna resumo das estatísticas."""
        summary = self.stats.copy()
        
        # Calcular taxas
        if summary["total_calls"] > 0:
            summary["success_rate"] = (
                summary["successful_calls"] / summary["total_calls"] * 100
            )
            summary["avg_cost_per_call"] = (
                summary["total_cost"] / summary["total_calls"]
            )
            summary["avg_tokens_per_call"] = (
                summary["total_tokens"] / summary["total_calls"]
            )
        
        # Calcular por provedor
        for provider_data in summary["providers"].values():
            if provider_data["calls"] > 0:
                provider_data["success_rate"] = (
                    provider_data["successes"] / provider_data["calls"] * 100
                )
                provider_data["avg_cost_per_call"] = (
                    provider_data["total_cost"] / provider_data["calls"]
                )
        
        return summary
    
    def save_daily_report(self):
        """Salva relatório diário de métricas."""
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": self.get_stats_summary(),
            "timestamp": datetime.now().isoformat()
        }
        
        report_file = self.log_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Reset estatísticas diárias (mantém acumulado para o mês)
        # Em produção, você pode querer manter histórico
        
        return report_file


# Instância global
metrics_logger = MetricsLogger()