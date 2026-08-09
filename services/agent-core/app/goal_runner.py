from .executor import Executor
from .goals import GoalStatus, GoalStore
from .planner import Planner


class GoalRunner:
    def __init__(self, goal_store: GoalStore):
        self.goal_store = goal_store
        self.planner = Planner()
        self.executor = Executor()

    async def run(self, goal_id: str) -> dict:
        goal = self.goal_store.get(goal_id)
        if not goal:
            raise ValueError("Goal not found")

        self.goal_store.update_status(goal.id, GoalStatus.ACTIVE)
        steps = await self.planner.plan(goal.objective)
        results = []
        for step in steps:
            result = await self.executor.execute(step)
            results.append({
                "order": step.order,
                "title": step.title,
                "objective": step.objective,
                "status": result.status,
                "output": result.output,
            })

        status = GoalStatus.COMPLETED if steps else GoalStatus.FAILED
        self.goal_store.update_status(goal.id, status)
        return {"goal_id": goal.id, "status": status.value, "steps": results}
