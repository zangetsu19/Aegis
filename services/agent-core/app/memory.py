from pathlib import Path
import sqlite3
from datetime import datetime, timezone


class MemoryStore:
    """Small durable memory layer for AEGIS v0.1.

    This is intentionally simple so the storage backend can later be replaced
    by PostgreSQL + vector/graph memory without changing the agent API.
    """

    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        self.db.commit()

    def add(self, session_id: str, role: str, content: str) -> None:
        self.db.execute(
            "INSERT INTO memories(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.now(timezone.utc).isoformat()),
        )
        self.db.commit()

    def recent(self, session_id: str, limit: int = 20) -> list[dict[str, str]]:
        rows = self.db.execute(
            "SELECT role, content FROM memories WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        return [{"role": role, "content": content} for role, content in reversed(rows)]
