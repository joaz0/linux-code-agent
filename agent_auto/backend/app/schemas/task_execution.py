"""
Schemas para execução e resultado de tasks
Define estrutura de retorno do agente
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TaskResult(BaseModel):
    """
    Resultado da execução de uma task
    Retornado pelo Agent após completar (ou falhar)
    """
    success: bool = Field(
        ...,
        description="Se a task foi completada com sucesso"
    )
    
    output: str = Field(
        ...,
        description="Saída principal da execução"
    )
    
    error: Optional[str] = Field(
        default=None,
        description="Mensagem de erro (se falhou)"
    )
    
    actions_taken: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de ações executadas pelo agente"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "output": "Arquivo README.md criado com sucesso",
                "error": None,
                "actions_taken": [
                    {
                        "tool": "write_file",
                        "params": {
                            "path": "README.md",
                            "content": "# My Project\n\nDocumentation here"
                        },
                        "result": "File written successfully"
                    }
                ]
            }
        }


class ActionExecution(BaseModel):
    """
    Detalhes de uma ação executada
    Usado internamente pelo executor
    """
    tool: str = Field(..., description="Nome da tool executada")
    params: Dict[str, Any] = Field(..., description="Parâmetros usados")
    result: str = Field(..., description="Resultado da execução")
    duration_ms: Optional[float] = Field(
        default=None,
        description="Tempo de execução em milissegundos"
    )
    success: bool = Field(default=True, description="Se executou com sucesso")
    error: Optional[str] = Field(default=None, description="Erro se falhou")