from app.core.registry import ToolRegistry

class Executor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_name: str, params: dict):
        tool = self.registry.get(tool_name)
        return tool.handler(**params)
