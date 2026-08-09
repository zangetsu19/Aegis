from agents import Agent, Runner

from .config import settings
from .memory import MemoryStore
from .tools import TOOLS


SYSTEM_INSTRUCTIONS = """You are AEGIS, an autonomous AI agent under the user's control.

Operate as a capable assistant that can reason, plan, use tools, remember useful
information, and break complex objectives into actionable tasks.

Rules:
- Be fast and concise when the request is simple.
- For complex goals, create a clear plan before taking actions.
- Never claim an action was completed unless it actually was.
- Treat external side effects, spending money, publishing, credential use,
  blockchain transactions, and destructive operations as approval-required.
- Prefer reusable knowledge and successful strategies over repeatedly starting
  from scratch.
"""


class AegisAgent:
    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self.agent = Agent(
            name="AEGIS",
            instructions=SYSTEM_INSTRUCTIONS,
            model=settings.openai_model,
            tools=TOOLS,
        )

    async def run(self, session_id: str, message: str):
        self.memory.add(session_id, "user", message)
        history = self.memory.recent(session_id)
        result = await Runner.run(
            self.agent,
            history,
            max_turns=settings.max_agent_turns,
        )
        self.memory.add(session_id, "assistant", result.final_output)
        return result

    def stream(self, session_id: str, message: str):
        self.memory.add(session_id, "user", message)
        history = self.memory.recent(session_id)
        return Runner.run_streamed(
            self.agent,
            history,
            max_turns=settings.max_agent_turns,
        )
