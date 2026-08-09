from dataclasses import dataclass
from urllib.parse import urlparse

from .planner import PlannedStep
from .web import WebResearchTool


@dataclass
class ExecutionResult:
    step: PlannedStep
    status: str
    output: str


class Executor:
    """Executes bounded tool actions selected by the planner."""

    def __init__(self):
        self.web = WebResearchTool()

    async def execute(self, step: PlannedStep) -> ExecutionResult:
        # The first real tool is deliberately explicit: a step must contain an
        # HTTP(S) URL before the executor will perform a network request.
        candidate = step.objective.strip()
        parsed = urlparse(candidate)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            try:
                result = await self.web.fetch(candidate)
                return ExecutionResult(
                    step=step,
                    status="completed",
                    output=f"Fetched {result.url}\n\n{result.text}",
                )
            except Exception as exc:
                return ExecutionResult(step=step, status="failed", output=f"Web fetch failed: {exc}")

        return ExecutionResult(
            step=step,
            status="ready",
            output=f"Step ready for execution: {step.title} — {step.objective}",
        )
