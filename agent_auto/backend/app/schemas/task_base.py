"""
Schema base para criação de tasks
Define a estrutura de entrada da API
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """
    Dados necessários para criar uma task
    Representa o input do usuário
    """
    objective: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="O que você quer que o agente faça",
        examples=[
            "Criar um arquivo README.md com documentação básica",
            "Listar todos os arquivos .py no diretório atual",
            "Fazer commit das mudanças com mensagem 'feat: nova feature'"
        ]
    )
    
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto adicional para ajudar o agente",
        examples=[
            {"project": "my-app", "language": "python"},
            {"directory": "/home/user/projects"},
            {"branch": "main"}
        ]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "objective": "Criar arquivo setup.py para o projeto",
                "context": {
                    "project_name": "linux-code-agent",
                    "version": "0.1.0",
                    "author": "Developer"
                }
            }
        }