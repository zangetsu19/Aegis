from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .agent import AegisAgent
from .config import settings
from .memory import MemoryStore
from .task_api import list_tasks

app = FastAPI(title=settings.app_name, version="0.2.0")
memory = MemoryStore(settings.memory_db_path)
aegis = AegisAgent(memory)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=100_000)


class ChatResponse(BaseModel):
    session_id: str
    output: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "aegis-agent-core", "version": "0.2.0"}


@app.get("/v1/tasks/{session_id}")
async def tasks(session_id: str):
    return {"session_id": session_id, "tasks": list_tasks(session_id)}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    result = await aegis.run(request.session_id, request.message)
    return ChatResponse(session_id=request.session_id, output=result.final_output)


@app.post("/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    result = aegis.stream(request.session_id, request.message)

    async def events():
        async for event in result.stream_events():
            if event.type != "raw_response_event":
                continue
            data = event.data
            if getattr(data, "type", None) == "response.output_text.delta":
                delta = getattr(data, "delta", "")
                if delta:
                    yield delta
        if result.final_output:
            memory.add(request.session_id, "assistant", result.final_output)

    return StreamingResponse(events(), media_type="text/plain; charset=utf-8")
