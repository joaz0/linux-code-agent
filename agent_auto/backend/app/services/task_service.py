"""
Task Service - Gerenciamento de estado e ciclo de vida das tasks
Responsável por: criar, atualizar, listar, cancelar tasks
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4
import threading

from app.schemas.task import TaskRequest
from app.schemas.task_status import TaskStatus, TaskState
from app.schemas.task_execution import TaskResult


class TaskService:
    """Gerenciador central de tasks do agente"""
    
    def __init__(self):
        self._tasks: Dict[str, TaskStatus] = {}
        self._lock = threading.Lock()
    
    def create_task(self, task_data: TaskRequest) -> TaskStatus:
        """
        Cria uma nova task e retorna seu status inicial
        
        Args:
            task_data: Dados da task (objetivo, contexto)
            
        Returns:
            TaskStatus inicial com ID único
        """
        task_id = str(uuid4())
        
        task_status = TaskStatus(
            id=task_id,
            objective=task_data.objective,
            context=task_data.context,
            state=TaskState.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            logs=[],
            steps=[],
            result=None
        )
        
        with self._lock:
            self._tasks[task_id] = task_status
        
        self._add_log(task_id, f"Task criada: {task_data.objective}")
        return task_status
    
    def get_task(self, task_id: str) -> Optional[TaskStatus]:
        """
        Busca uma task pelo ID
        
        Args:
            task_id: ID da task
            
        Returns:
            TaskStatus ou None se não encontrada
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def list_tasks(
        self, 
        state: Optional[TaskState] = None,
        limit: int = 50
    ) -> List[TaskStatus]:
        """
        Lista tasks com filtro opcional
        
        Args:
            state: Filtro por estado (opcional)
            limit: Máximo de tasks a retornar
            
        Returns:
            Lista de TaskStatus ordenada por data (mais recentes primeiro)
        """
        with self._lock:
            tasks = list(self._tasks.values())
        
        # Filtrar por estado se especificado
        if state:
            tasks = [t for t in tasks if t.state == state]
        
        # Ordenar por data de criação (mais recente primeiro)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks[:limit]
    
    def update_state(
        self, 
        task_id: str, 
        new_state: TaskState,
        log_message: Optional[str] = None
    ) -> bool:
        """
        Atualiza o estado de uma task
        
        Args:
            task_id: ID da task
            new_state: Novo estado
            log_message: Mensagem de log opcional
            
        Returns:
            True se atualizado, False se task não existe
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            task.state = new_state
            task.updated_at = datetime.utcnow()
        
        if log_message:
            self._add_log(task_id, log_message)
        
        return True
    
    def add_step(
        self, 
        task_id: str, 
        step_description: str
    ) -> bool:
        """
        Adiciona um passo executado à task
        
        Args:
            task_id: ID da task
            step_description: Descrição do passo
            
        Returns:
            True se adicionado, False se task não existe
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            task.steps.append({
                'timestamp': datetime.utcnow().isoformat(),
                'description': step_description
            })
            task.updated_at = datetime.utcnow()
        
        return True
    
    def complete_task(
        self, 
        task_id: str, 
        result: TaskResult
    ) -> bool:
        """
        Marca task como completa e armazena resultado
        
        Args:
            task_id: ID da task
            result: Resultado da execução
            
        Returns:
            True se completado, False se task não existe
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            task.state = TaskState.COMPLETED if result.success else TaskState.FAILED
            task.result = result
            task.updated_at = datetime.utcnow()
        
        status = "sucesso" if result.success else "falha"
        self._add_log(task_id, f"Task finalizada com {status}")
        
        return True
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancela uma task em execução
        
        Args:
            task_id: ID da task
            
        Returns:
            True se cancelada, False se não pode ser cancelada
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            # Só pode cancelar tasks pending ou running
            if task.state not in [TaskState.PENDING, TaskState.RUNNING]:
                return False
            
            task.state = TaskState.CANCELLED
            task.updated_at = datetime.utcnow()
        
        self._add_log(task_id, "Task cancelada pelo usuário")
        return True
    
    def _add_log(self, task_id: str, message: str) -> None:
        """
        Adiciona entrada de log à task (thread-safe)
        
        Args:
            task_id: ID da task
            message: Mensagem de log
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.logs.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'message': message
                })
    
    def get_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas gerais das tasks
        
        Returns:
            Dicionário com contadores por estado
        """
        with self._lock:
            stats = {
                'total': len(self._tasks),
                'pending': 0,
                'running': 0,
                'completed': 0,
                'failed': 0,
                'cancelled': 0
            }
            
            for task in self._tasks.values():
                state_name = task.state.value
                if state_name in stats:
                    stats[state_name] += 1
            
            return stats


# Singleton global
_task_service_instance: Optional[TaskService] = None


def get_task_service() -> TaskService:
    """
    Retorna instância singleton do TaskService
    Usado para dependency injection no FastAPI
    """
    global _task_service_instance
    if _task_service_instance is None:
        _task_service_instance = TaskService()
    return _task_service_instance