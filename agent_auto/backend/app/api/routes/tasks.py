"""
API Routes - Endpoints HTTP para gerenciamento de tasks
Responsável apenas por: receber requests, validar, chamar services, retornar responses
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends

from app.schemas.task import TaskRequest
from app.schemas.task_status import (
    TaskStatus, 
    TaskState, 
    TaskListResponse,
    TaskStatsResponse
)
from app.services.task_service import TaskService, get_task_service
from app.core.agent import Agent
from app.core.registry import Tool, ToolRegistry
from app.tools import fs, git, shell as shell_tools


router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_agent() -> Agent:
    """Dependency para obter instância do Agent"""
    registry = ToolRegistry()
    
    # Filesystem tools
    registry.register(Tool("read_file", "Lê o conteúdo de um arquivo de texto.", fs.read_file))
    registry.register(Tool("write_file", "Escreve (ou sobrescreve) conteúdo em um arquivo.", fs.write_file))
    registry.register(Tool("list_files", "Lista arquivos recursivamente em um diretório.", fs.list_files))
    
    # Git tools
    registry.register(Tool("git_status", "Obtém o status do repositório git.", git.git_status))
    registry.register(Tool("git_commit", "Cria um commit com uma mensagem.", git.git_commit))

    # Shell tools
    registry.register(Tool("shell", "Executa um comando shell.", shell_tools.shell_tool))
    
    return Agent(registry)


@router.post(
    "",
    response_model=TaskStatus,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova task",
    description="Cria uma task e retorna seu status inicial. A execução é assíncrona."
)
async def create_task(
    task_data: TaskRequest,
    background_tasks: BackgroundTasks,
    task_service: TaskService = Depends(get_task_service),
    agent: Agent = Depends(get_agent)
) -> TaskStatus:
    """
    Cria uma nova task para o agente executar
    
    - **objective**: O que você quer que o agente faça
    - **context**: Informações adicionais (opcional)
    
    A task é executada em background. Use GET /tasks/{id} para acompanhar.
    """
    # Criar task no service
    task_status = task_service.create_task(task_data)
    
    # Agendar execução em background
    background_tasks.add_task(
        _execute_task_background,
        task_status.id,
        task_data,
        task_service,
        agent
    )
    
    return task_status


@router.get(
    "",
    response_model=TaskListResponse,
    summary="Listar tasks",
    description="Lista todas as tasks com filtro opcional por estado"
)
async def list_tasks(
    state: Optional[TaskState] = None,
    limit: int = 50,
    task_service: TaskService = Depends(get_task_service)
) -> TaskListResponse:
    """
    Lista tasks do sistema
    
    - **state**: Filtrar por estado (pending, running, completed, failed, cancelled)
    - **limit**: Máximo de tasks a retornar (padrão: 50)
    """
    tasks = task_service.list_tasks(state=state, limit=limit)
    
    return TaskListResponse(
        tasks=tasks,
        total=len(tasks)
    )


@router.get(
    "/stats",
    response_model=TaskStatsResponse,
    summary="Estatísticas das tasks",
    description="Retorna contadores por estado"
)
async def get_stats(
    task_service: TaskService = Depends(get_task_service)
) -> TaskStatsResponse:
    """
    Obtém estatísticas gerais das tasks
    
    Retorna contadores de tasks por estado
    """
    stats = task_service.get_stats()
    return TaskStatsResponse(**stats)


@router.get(
    "/{task_id}",
    response_model=TaskStatus,
    summary="Obter status de uma task",
    description="Retorna o status completo e logs de uma task específica"
)
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
) -> TaskStatus:
    """
    Busca uma task pelo ID
    
    - **task_id**: UUID da task
    
    Retorna 404 se a task não existir
    """
    task = task_service.get_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} não encontrada"
        )
    
    return task


@router.post(
    "/{task_id}/cancel",
    response_model=TaskStatus,
    summary="Cancelar task",
    description="Cancela uma task em execução ou pendente"
)
async def cancel_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
) -> TaskStatus:
    """
    Cancela uma task
    
    - **task_id**: UUID da task
    
    Só pode cancelar tasks pending ou running.
    Retorna 404 se não encontrada, 400 se não pode ser cancelada.
    """
    task = task_service.get_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} não encontrada"
        )
    
    success = task_service.cancel_task(task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} não pode ser cancelada (estado atual: {task.state})"
        )
    
    # Retornar status atualizado
    return task_service.get_task(task_id)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar task",
    description="Remove uma task do histórico (não implementado ainda)"
)
async def delete_task(task_id: str):
    """
    Deleta uma task do histórico
    
    TODO: Implementar quando tiver persistência
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Deleção de tasks ainda não implementada"
    )


# ========================================
# FUNÇÕES AUXILIARES (não são endpoints)
# ========================================

async def _execute_task_background(
    task_id: str,
    task_data: TaskRequest,
    task_service: TaskService,
    agent: Agent
) -> None:
    """
    Executa a task em background
    Atualiza o status conforme progride
    
    Args:
        task_id: ID da task
        task_data: Dados da task
        task_service: Service de tasks
        agent: Instância do agente
    """
    try:
        # Marcar como running
        task_service.update_state(
            task_id,
            TaskState.RUNNING,
            "Iniciando execução..."
        )
        
        # Formatar o prompt para o agente
        prompt = f"Objetivo: {task_data.objective}"
        if task_data.context:
            prompt += f"\nContexto: {task_data.context}"
            
        # Executar via agente
        result = agent.run(prompt)
        
        # Registrar passos executados
        if hasattr(result, 'actions_taken'):
            for action in result.actions_taken:
                task_service.add_step(
                    task_id,
                    f"{action['tool']}: {action['params']}"
                )
        
        # Marcar como completa
        task_service.complete_task(task_id, result)
        
    except Exception as e:
        # Em caso de erro, marcar como failed
        task_service.update_state(
            task_id,
            TaskState.FAILED,
            f"Erro na execução: {str(e)}"
        )
        
        # Criar resultado de falha
        from app.schemas.task_execution import TaskResult
        error_result = TaskResult(
            success=False,
            output="",
            error=str(e),
            actions_taken=[]
        )
        task_service.complete_task(task_id, error_result)