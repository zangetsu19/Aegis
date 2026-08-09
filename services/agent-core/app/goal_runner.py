from .executor import Executor
from .goals import GoalStatus, GoalStore
from .planner import Planner
from .research_agent import ResearchAgent
from .research_memory import ResearchMemory


class GoalRunner:
    def __init__(self, goal_store: GoalStore, memory_path: str):
        self.goal_store = goal_store
        self.planner = Planner()
        self.executor = Executor()
        self.research = ResearchAgent(ResearchMemory(memory_path))

    async def run(self, goal_id: str) -> dict:
        goal = self.goal_store.get(goal_id)
        if not goal:
            raise ValueError("Goal not found")

        self.goal_store.update_status(goal.id, GoalStatus.ACTIVE)
        steps = await self.planner.plan(goal.objective)
        results = []
        research_context = []

        for step in steps:
            title = step.title.lower()
            objective = step.objective.strip()
            if title.startswith(("research", "search", "find")):
                result = await self.research.research(goal.session_id, objective)
                research_context.append(result)
                results.append({
                    "order": step.order,
                    "title": step.title,
                    "objective": step.objective,
                    "status": "completed" if result["sources"] else "failed",
                    "output": result["report"],
                    "sources": result["sources"],
                })
            else:
                result = await self.executor.execute(step)
                results.append({
                    "order": step.order,
                    "title": step.title,
                    "objective": step.objective,
                    "status": result.status,
                    "output": result.output,
                })

        completed = sum(1 for item in results if item["status"] == "completed")
        status = GoalStatus.COMPLETED if results and completed == len(results) else GoalStatus.FAILED
        self.goal_store.update_status(goal.id, status)
        return {
            "goal_id": goal.id,
            "status": status.value,
            "steps": results,
            "research_context": research_context,
        }
