from __future__ import annotations

from .evaluator import OutcomeEvaluator
from .skill_learning import SkillLearner, SkillStore


class SelfImprovementLoop:
    """Evaluate an outcome and turn sufficiently strong results into reusable skills."""

    def __init__(self, memory_path: str):
        self.evaluator = OutcomeEvaluator()
        self.learner = SkillLearner(SkillStore(memory_path))

    async def process(self, session_id: str, objective: str, outcome: str, execution_status: str) -> dict:
        evaluation = await self.evaluator.evaluate(objective, outcome)
        success = execution_status == "completed" and evaluation["success"] and evaluation["score"] >= 0.6
        learning = await self.learner.learn(session_id, objective, outcome, success)
        return {"evaluation": evaluation, "learning": learning, "success": success}
