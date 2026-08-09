from dataclasses import dataclass

from .planner import PlannedStep


@dataclass
class ExecutionResult:
    step: PlannedStep
    status: str
    output: str


class Executor:
    """Initial deterministic executor. Tool-backed execution is added incrementally."""

    async def execute(self, step: PlannedStep) -> ExecutionResult:
        # v0.4 intentionally does not perform external side effects.
        # This makes the planning/execution boundary explicit before web and
        # other tools are enabled.
        return ExecutionResult(
            step=step,
            status="ready",
            output=f"Step ready for execution: {step.title} — {step.objective}",
        )
