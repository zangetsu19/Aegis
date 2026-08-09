from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agent import AegisAgent
from .config import settings
from .memory import MemoryStore

app = FastAPI(title=settings.app_name, version="0.1.0")
memory = MemoryStore(settings.memory_db_path)
aegis = AegisAgent(memory)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=100_000)


class ChatResponse(BaseModel):
    session_id: str
    output: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "aegis-agent-core", "version": "0.1.0"}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    result = await aegis.run(request.session_id, request.message)
    return ChatResponse(session_id=request.session_id, output=result.final_output)
