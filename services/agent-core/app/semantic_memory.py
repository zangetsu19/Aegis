from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from openai import AsyncOpenAI

from .config import settings


class SemanticMemory:
    """Persistent semantic memory backed by SQLite and OpenAI embeddings."""

    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS semantic_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        self.db.commit()

    @staticmethod
    def cosine(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0

    def add(self, session_id: str, kind: str, text: str, embedding: list[float]) -> None:
        self.db.execute(
            "INSERT INTO semantic_memories(session_id, kind, text, embedding, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, kind, text, json.dumps(embedding), datetime.now(timezone.utc).isoformat()),
        )
        self.db.commit()

    def search(self, session_id: str, embedding: list[float], limit: int = 8) -> list[dict]:
        rows = self.db.execute(
            "SELECT id, kind, text, embedding, created_at FROM semantic_memories WHERE session_id = ?",
            (session_id,),
        ).fetchall()
        ranked = []
        for memory_id, kind, text, vector, created_at in rows:
            score = self.cosine(embedding, json.loads(vector))
            ranked.append((score, memory_id, kind, text, created_at))
        ranked.sort(reverse=True, key=lambda x: x[0])
        return [
            {"id": r[1], "kind": r[2], "text": r[3], "score": r[0], "created_at": r[4]}
            for r in ranked[:limit]
        ]


class SemanticMemoryService:
    def __init__(self, memory: SemanticMemory):
        self.memory = memory
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(model=settings.embedding_model, input=text)
        return response.data[0].embedding

    async def remember(self, session_id: str, kind: str, text: str) -> str:
        embedding = await self.embed(text)
        self.memory.add(session_id, kind, text, embedding)
        return text

    async def recall(self, session_id: str, query: str, limit: int = 8) -> list[dict]:
        embedding = await self.embed(query)
        return self.memory.search(session_id, embedding, limit)
