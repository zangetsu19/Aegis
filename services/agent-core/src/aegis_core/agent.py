from agents import Agent, Runner


class AegisAgent:
    """Minimal AEGIS agent facade; orchestration will grow around this boundary."""

    def __init__(self) -> None:
        self.agent = Agent(
            name="AEGIS",
            instructions=(
                "You are AEGIS, an autonomous personal AI agent. "
                "Be concise, accurate, transparent about uncertainty, and action-oriented. "
                "Do not claim to have completed an action unless a tool actually completed it. "
                "Consequential actions require explicit user approval."
            ),
        )

    async def run(self, message: str) -> str:
        result = await Runner.run(self.agent, message)
        return result.final_output
