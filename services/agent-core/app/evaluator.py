from __future__ import annotations

import json
from agents import Agent, Runner
from .config import settings


class OutcomeEvaluator:
    def __init__(self):
        self.agent = Agent(
            name="AEGIS Outcome Evaluator",
            instructions=("Evaluate an execution result against its objective. Return JSON with success (boolean), score (0-1), reason, and retry_recommendation. Be conservative: partial or unsupported results are not full success."),
            model=settings.openai_model,
        )

    async def evaluate(self, objective: str, outcome: str) -> dict:
        result = await Runner.run(self.agent, f"Objective: {objective}\nOutcome:\n{outcome[:16000]}", max_turns=1)
        try:
            data = json.loads(str(result.final_output))
        except (ValueError, TypeError):
            return {"success": False, "score": 0, "reason": "invalid evaluator output", "retry_recommendation": "replan"}
        return {"success": bool(data.get("success")), "score": float(data.get("score", 0)), "reason": str(data.get("reason", "")), "retry_recommendation": str(data.get("retry_recommendation", "none"))}
