from dataclasses import dataclass
from typing import Any

from agents import Agent, Runner

from .config import settings


@dataclass
class PlannedStep:
    title: str
    objective: str
    order: int


class Planner:
    """Converts a user objective into a small, executable plan."""

    def __init__(self):
        self.agent = Agent(
            name="AEGIS Planner",
            instructions=(
                "You are the planning component of AEGIS. Break a complex objective "
                "into 2-8 concrete, independently executable steps. Prefer simple "
                "steps with explicit outcomes. Do not claim to execute anything. "
                "Return JSON with a 'steps' array. Each item must contain 'title', "
                "'objective', and 'order'."
            ),
            model=settings.openai_model,
        )

    async def plan(self, objective: str) -> list[PlannedStep]:
        result = await Runner.run(self.agent, objective, max_turns=2)
        data: Any = result.final_output
        if isinstance(data, dict):
            raw = data.get("steps", [])
        else:
            import json
            try:
                raw = json.loads(str(data)).get("steps", [])
            except (ValueError, TypeError):
                raw = []

        steps: list[PlannedStep] = []
        for index, item in enumerate(raw, start=1):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            step_objective = str(item.get("objective", "")).strip()
            if title and step_objective:
                steps.append(PlannedStep(title, step_objective, index))
        return steps[:8]
