from dataclasses import dataclass
from urllib.parse import urlparse

from .planner import PlannedStep
from .research import ResearchTool
from .web import WebResearchTool


@dataclass
class ExecutionResult:
    step: PlannedStep
    status: str
    output: str


class Executor:
    """Executes bounded research and web actions selected by the planner."""

    def __init__(self):
        self.web = WebResearchTool()
        self.research = ResearchTool()

    async def execute(self, step: PlannedStep) -> ExecutionResult:
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

        # Research steps are recognized explicitly to avoid turning arbitrary
        # planner text into unrestricted network activity.
        if step.title.lower().startswith(("research", "search", "find")):
            try:
                results = await self.research.search(candidate)
                if not results:
                    return ExecutionResult(step=step, status="completed", output="No search results found.")
                lines = [f"{i}. {r.title}\n   {r.url}\n   {r.snippet}" for i, r in enumerate(results, 1)]
                return ExecutionResult(
                    step=step,
                    status="completed",
                    output="Search results:\n" + "\n".join(lines),
                )
            except Exception as exc:
                return ExecutionResult(step=step, status="failed", output=f"Research failed: {exc}")

        return ExecutionResult(
            step=step,
            status="ready",
            output=f"Step ready for execution: {step.title} — {step.objective}",
        )
