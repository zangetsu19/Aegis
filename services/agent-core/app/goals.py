from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4


class GoalStatus(StrEnum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Goal:
    id: str
    session_id: str
    objective: str
    status: GoalStatus
    created_at: str


class GoalStore:
    """Small SQLite-backed goal store; replaceable by the future persistence service."""

    def __init__(self, db_path: str):
        import sqlite3
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS goals (id TEXT PRIMARY KEY, session_id TEXT NOT NULL, objective TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL)"
            )

    def create(self, session_id: str, objective: str) -> Goal:
        goal = Goal(str(uuid4()), session_id, objective, GoalStatus.PLANNING, datetime.now(timezone.utc).isoformat())
        import sqlite3
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO goals VALUES (?, ?, ?, ?, ?)", (goal.id, goal.session_id, goal.objective, goal.status.value, goal.created_at))
        return goal

    def get(self, goal_id: str) -> Goal | None:
        import sqlite3
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT id, session_id, objective, status, created_at FROM goals WHERE id = ?", (goal_id,)).fetchone()
        return Goal(*row[:3], GoalStatus(row[3]), row[4]) if row else None

    def update_status(self, goal_id: str, status: GoalStatus) -> None:
        import sqlite3
        with sqlite3.connect(self.db_path) as db:
            db.execute("UPDATE goals SET status = ? WHERE id = ?", (status.value, goal_id))

    def list(self, session_id: str) -> list[dict]:
        import sqlite3
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT id, objective, status, created_at FROM goals WHERE session_id = ? ORDER BY created_at DESC", (session_id,)).fetchall()
        return [{"id": r[0], "objective": r[1], "status": r[2], "created_at": r[3]} for r in rows]
