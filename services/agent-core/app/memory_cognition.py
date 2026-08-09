from __future__ import annotations

import json

from agents import Agent, Runner

from .config import settings
from .semantic_memory import SemanticMemoryService


class MemoryCognition:
    """Decides what is worth remembering and recalls relevant context."""

    def __init__(self, service: SemanticMemoryService):
        self.service = service
        self.judge = Agent(
            name="AEGIS Memory Judge",
            instructions=(
                "Decide whether text contains durable information worth remembering. "
                "Return JSON with remember (boolean), kind (fact|preference|goal|project|research|task), "
                "and importance from 0 to 1. Remember stable facts, preferences, project decisions, "
                "research findings, and commitments. Do not remember greetings or transient filler."
            ),
            model=settings.openai_model,
        )

    async def consider(self, session_id: str, text: str) -> dict:
        result = await Runner.run(self.judge, text, max_turns=1)
        try:
            decision = json.loads(str(result.final_output))
        except (ValueError, TypeError):
            decision = {"remember": False, "kind": "fact", "importance": 0}
        if bool(decision.get("remember")) and float(decision.get("importance", 0)) >= 0.6:
            decision["stored"] = await self.service.remember(
                session_id, str(decision.get("kind", "fact")), text
            )
        else:
            decision["stored"] = None
        return decision

    async def recall(self, session_id: str, query: str, limit: int = 8) -> list[dict]:
        return await self.service.recall(session_id, query, limit)
