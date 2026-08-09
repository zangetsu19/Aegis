from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from agents import Agent, Runner

from .config import settings


class SkillStore:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("""CREATE TABLE IF NOT EXISTS learned_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            name TEXT NOT NULL,
            strategy TEXT NOT NULL,
            success_count INTEGER NOT NULL DEFAULT 0,
            failure_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")
        self.db.commit()

    def upsert(self, session_id: str, name: str, strategy: str, success: bool) -> None:
        now = datetime.now(timezone.utc).isoformat()
        row = self.db.execute(
            "SELECT id, success_count, failure_count FROM learned_skills WHERE session_id=? AND name=?",
            (session_id, name),
        ).fetchone()
        if row:
            self.db.execute(
                "UPDATE learned_skills SET strategy=?, success_count=?, failure_count=?, updated_at=? WHERE id=?",
                (strategy, row[1] + int(success), row[2] + int(not success), now, row[0]),
            )
        else:
            self.db.execute(
                "INSERT INTO learned_skills(session_id,name,strategy,success_count,failure_count,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (session_id, name, strategy, int(success), int(not success), now, now),
            )
        self.db.commit()

    def list(self, session_id: str, limit: int = 20) -> list[dict]:
        rows = self.db.execute(
            "SELECT name,strategy,success_count,failure_count,updated_at FROM learned_skills WHERE session_id=? ORDER BY (success_count-failure_count) DESC, updated_at DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        return [{"name": r[0], "strategy": r[1], "success_count": r[2], "failure_count": r[3], "updated_at": r[4]} for r in rows]


class SkillLearner:
    def __init__(self, store: SkillStore):
        self.store = store
        self.agent = Agent(
            name="AEGIS Skill Learner",
            instructions=(
                "Analyze an executed task and extract a reusable strategy. Return JSON with "
                "name, strategy, and confidence (0-1). Only propose reusable strategies. "
                "Never store secrets, credentials, or private data."
            ),
            model=settings.openai_model,
        )

    async def learn(self, session_id: str, objective: str, outcome: str, success: bool) -> dict:
        result = await Runner.run(self.agent, f"Objective: {objective}\nSuccess: {success}\nOutcome: {outcome[:12000]}", max_turns=1)
        try:
            data = json.loads(str(result.final_output))
        except (ValueError, TypeError):
            return {"learned": False, "reason": "invalid learner output"}
        if float(data.get("confidence", 0)) < 0.7 or not data.get("name") or not data.get("strategy"):
            return {"learned": False, "reason": "insufficient reusable strategy"}
        self.store.upsert(session_id, str(data["name"]), str(data["strategy"]), success)
        return {"learned": True, "name": data["name"], "strategy": data["strategy"], "success": success}
