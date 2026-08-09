from fastapi import APIRouter
from pydantic import BaseModel, Field

from .config import settings
from .semantic_memory import SemanticMemory, SemanticMemoryService

router = APIRouter(prefix="/v1/memory", tags=["memory"])
service = SemanticMemoryService(SemanticMemory(settings.memory_db_path))


class RememberRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    kind: str = Field(default="fact", max_length=100)
    text: str = Field(min_length=1, max_length=20_000)


@router.post("")
async def remember(request: RememberRequest):
    return {"stored": await service.remember(request.session_id, request.kind, request.text)}


@router.get("/{session_id}")
async def recall(session_id: str, q: str = "", limit: int = 8):
    return {"session_id": session_id, "results": await service.recall(session_id, q, min(max(limit, 1), 20))}
