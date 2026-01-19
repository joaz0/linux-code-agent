from fastapi import APIRouter
from app.schemas.task import TaskRequest
from app.core.agent import Agent
from app.core.registry import ToolRegistry, Tool
from app.tools import fs, git, shell

router = APIRouter()

# Create a tool registry
registry = ToolRegistry()

# Register tools from fs.py
registry.register(Tool("read_file", "Reads a file", fs.read_file))
registry.register(Tool("write_file", "Writes a file", fs.write_file))
registry.register(Tool("list_files", "Lists files in a directory", fs.list_files))

# Register tools from git.py
registry.register(Tool("git_status", "Gets git status", git.git_status))
registry.register(Tool("git_commit", "Commits changes", git.git_commit))

# Register tools from shell.py
registry.register(Tool("shell_tool", "Executes a shell command", shell.shell_tool))
registry.register(Tool("run_command", "Runs a command", shell.run_command))


# Create an agent
agent = Agent(registry)

@router.post("/execute")
def execute(req: TaskRequest):
    return agent.run(req.objective)