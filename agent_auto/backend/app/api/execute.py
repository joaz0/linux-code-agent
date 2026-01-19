from fastapi import APIRouter
from app.schemas.task import TaskRequest
from app.agent.executor import execute_task

router = APIRouter()

@router.post("/execute")
def execute(req: TaskRequest):
    return execute_task(req)
