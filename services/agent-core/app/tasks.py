from pathlib import Path
import sqlite3
from datetime import datetime, timezone


class TaskStore:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                title TEXT NOT NULL,
                objective TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            )"""
        )
        self.db.commit()

    def create(self, session_id: str, title: str, objective: str) -> int:
        cur = self.db.execute(
            "INSERT INTO tasks(session_id, title, objective, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
            (session_id, title, objective, datetime.now(timezone.utc).isoformat()),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def list(self, session_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT id, title, objective, status, created_at FROM tasks WHERE session_id = ? ORDER BY id DESC",
            (session_id,),
        ).fetchall()
        return [
            {"id": r[0], "title": r[1], "objective": r[2], "status": r[3], "created_at": r[4]}
            for r in rows
        ]
