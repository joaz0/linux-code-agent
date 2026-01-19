from core.executor import Executor
from core.planner import plan

class Agent:
    def __init__(self, registry):
        self.executor = Executor(registry)
        self.registry = registry

    def run(self, task: str):
        decision = plan(task, self.registry.list())
        result = self.executor.execute(
            decision["tool"],
            decision.get("params", {})
        )
        return result
