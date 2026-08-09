from fastapi import FastAPI
from pydantic import BaseModel

from .agent import AegisAgent

app = FastAPI(title="AEGIS Agent Core", version="0.1.0")
agent = AegisAgent()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "aegis-agent-core"}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(response=await agent.run(request.message))
