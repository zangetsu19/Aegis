from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class ResearchMemory:
    """Durable store for research findings and source metadata."""

    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS research_findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                query TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                snippet TEXT,
                content TEXT,
                created_at TEXT NOT NULL
            )"""
        )
        self.db.commit()

    def save(self, session_id: str, query: str, title: str, url: str, snippet: str = "", content: str = "") -> None:
        self.db.execute(
            "INSERT INTO research_findings(session_id, query, title, url, snippet, content, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, query, title, url, snippet, content, datetime.now(timezone.utc).isoformat()),
        )
        self.db.commit()

    def search(self, session_id: str, query: str, limit: int = 10) -> list[dict[str, str]]:
        rows = self.db.execute(
            "SELECT title, url, snippet, content FROM research_findings WHERE session_id = ? AND (query LIKE ? OR title LIKE ? OR snippet LIKE ?) ORDER BY id DESC LIMIT ?",
            (session_id, f"%{query}%", f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        return [
            {"title": title, "url": url, "snippet": snippet or "", "content": content or ""}
            for title, url, snippet, content in rows
        ]
