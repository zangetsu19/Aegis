from fastapi import APIRouter
from pydantic import BaseModel, Field

from .config import settings
from .research_agent import ResearchAgent
from .research_memory import ResearchMemory

router = APIRouter(prefix="/v1/research", tags=["research"])
agent = ResearchAgent(ResearchMemory(settings.memory_db_path))


class ResearchRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    query: str = Field(min_length=2, max_length=10_000)


@router.post("")
async def research(request: ResearchRequest):
    return await agent.research(request.session_id, request.query)


@router.get("/{session_id}")
async def research_memory(session_id: str, q: str = "", limit: int = 10):
    return {"session_id": session_id, "results": agent.memory.search(session_id, q, min(max(limit, 1), 50))}
