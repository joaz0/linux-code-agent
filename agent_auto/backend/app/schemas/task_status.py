"""
Schemas para status e estado das tasks
Define os estados possíveis e estrutura de status
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.task_execution import TaskResult


class TaskState(str, Enum):
    """Estados possíveis de uma task"""
    PENDING = "pending"       # Criada, aguardando execução
    RUNNING = "running"       # Em execução
    COMPLETED = "completed"   # Completada com sucesso
    FAILED = "failed"         # Falhou durante execução
    CANCELLED = "cancelled"   # Cancelada pelo usuário


class TaskLogEntry(BaseModel):
    """Entrada individual de log"""
    timestamp: str = Field(..., description="ISO timestamp do log")
    message: str = Field(..., description="Mensagem de log")


class TaskStep(BaseModel):
    """Passo executado durante a task"""
    timestamp: str = Field(..., description="ISO timestamp do passo")
    description: str = Field(..., description="Descrição do passo")


class TaskStatus(BaseModel):
    """
    Status completo de uma task
    Representa o estado atual e histórico
    """
    id: str = Field(..., description="ID único da task (UUID)")
    objective: str = Field(..., description="Objetivo original da task")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto adicional fornecido"
    )
    
    state: TaskState = Field(..., description="Estado atual da task")
    
    created_at: datetime = Field(..., description="Data/hora de criação")
    updated_at: datetime = Field(..., description="Data/hora da última atualização")
    
    logs: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Histórico de logs da execução"
    )
    
    steps: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Passos executados"
    )
    
    result: Optional[TaskResult] = Field(
        default=None,
        description="Resultado final (quando completa ou falha)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "objective": "Criar arquivo README.md com documentação",
                "context": {"project": "my-app"},
                "state": "completed",
                "created_at": "2025-01-18T10:00:00Z",
                "updated_at": "2025-01-18T10:00:15Z",
                "logs": [
                    {
                        "timestamp": "2025-01-18T10:00:00Z",
                        "message": "Task criada"
                    },
                    {
                        "timestamp": "2025-01-18T10:00:15Z",
                        "message": "Task finalizada com sucesso"
                    }
                ],
                "steps": [
                    {
                        "timestamp": "2025-01-18T10:00:10Z",
                        "description": "Executado: write_file README.md"
                    }
                ],
                "result": {
                    "success": True,
                    "output": "Arquivo criado com sucesso",
                    "error": None
                }
            }
        }


class TaskListResponse(BaseModel):
    """Response para listagem de tasks"""
    tasks: List[TaskStatus] = Field(..., description="Lista de tasks")
    total: int = Field(..., description="Total de tasks retornadas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [],
                "total": 0
            }
        }


class TaskStatsResponse(BaseModel):
    """Response com estatísticas das tasks"""
    total: int = Field(..., description="Total de tasks")
    pending: int = Field(default=0, description="Tasks pendentes")
    running: int = Field(default=0, description="Tasks em execução")
    completed: int = Field(default=0, description="Tasks completadas")
    failed: int = Field(default=0, description="Tasks que falharam")
    cancelled: int = Field(default=0, description="Tasks canceladas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 10,
                "pending": 2,
                "running": 1,
                "completed": 5,
                "failed": 1,
                "cancelled": 1
            }
        }