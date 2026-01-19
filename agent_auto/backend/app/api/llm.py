# app/api/llm.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional

from app.core.planner import Planner
from app.core.multi_llm import ComplexityLevel
from app.core.aws_toolkit import AWSToolkitDetector

router = APIRouter()


@router.get("/providers")
async def get_providers():
    """Retorna provedores LLM disponíveis."""
    planner = Planner()
    
    return {
        "available_providers": planner.multi_provider.get_available_providers(),
        "aws_toolkit_detected": planner.aws_detector.detect_credentials() if planner.aws_detector else False
    }


@router.get("/metrics")
async def get_metrics():
    """Retorna métricas de uso dos LLMs."""
    planner = Planner()
    
    return {
        "llm_metrics": planner.get_metrics(),
        "timestamp": datetime.now().isoformat()
    }


@router.post("/analyze")
async def analyze_task(task: str):
    """Analiza complexidade de uma tarefa."""
    planner = Planner()
    
    complexity = planner.multi_provider._estimate_complexity(task)
    cost_estimate = planner.multi_provider.get_cost_estimate(task)
    
    return {
        "task": task,
        "complexity": complexity.value,
        "recommended_provider": planner.multi_provider.select_provider(complexity),
        "cost_estimate_usd": cost_estimate,
        "word_count": len(task.split())
    }


@router.post("/test-provider")
async def test_provider(provider: str, test_prompt: str = "Hello, how are you?"):
    """Testa um provedor específico."""
    planner = Planner()
    
    if provider not in planner.multi_provider.get_available_providers():
        raise HTTPException(
            status_code=400,
            detail=f"Provider {provider} não disponível. Use: {planner.multi_provider.get_available_providers()}"
        )
    
    try:
        # Força uso do provider especificado
        result = planner.plan(
            task=test_prompt,
            tools={"test": "Test tool"},
            force_provider=provider
        )
        
        return {
            "provider": provider,
            "success": True,
            "response": result,
            "metadata": result.get("_metadata", {})
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao testar provider {provider}: {str(e)}"
        )


@router.get("/aws-status")
async def get_aws_status():
    """Verifica status das credenciais AWS."""
    detector = AWSToolkitDetector()
    
    return {
        "aws_toolkit_available": detector.vscode_aws_path is not None,
        "aws_credentials_detected": detector.detect_credentials(),
        "aws_cli_profiles": detector.aws_profiles_path.exists(),
        "recommended_profile": "default"
    }


@router.post("/force-provider")
async def force_provider(task: str, provider: str):
    """Força uso de um provedor específico."""
    planner = Planner()
    
    if provider not in planner.multi_provider.get_available_providers():
        raise HTTPException(
            status_code=400,
            detail=f"Provider {provider} não disponível"
        )
    
    result = planner.plan(task, tools={"shell": "Execute shell commands"}, force_provider=provider)
    
    return {
        "task": task,
        "forced_provider": provider,
        "result": result,
        "metadata": result.get("_metadata", {})
    }


# Adicionar import
from datetime import datetime