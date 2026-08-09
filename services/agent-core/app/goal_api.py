from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .config import settings
from .goal_runner import GoalRunner
from .goals import GoalStatus, GoalStore

router = APIRouter(prefix="/v1/goals", tags=["goals"])
goal_store = GoalStore(settings.memory_db_path)
goal_runner = GoalRunner(goal_store)


class GoalRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=3, max_length=20_000)


class GoalStatusRequest(BaseModel):
    status: GoalStatus


@router.post("")
async def create_goal(request: GoalRequest):
    goal = goal_store.create(request.session_id, request.objective)
    return {"id": goal.id, "session_id": goal.session_id, "objective": goal.objective, "status": goal.status.value, "created_at": goal.created_at}


@router.get("/{session_id}")
async def list_goals(session_id: str):
    return {"session_id": session_id, "goals": goal_store.list(session_id)}


@router.patch("/{goal_id}")
async def update_goal(goal_id: str, request: GoalStatusRequest):
    goal_store.update_status(goal_id, request.status)
    return {"id": goal_id, "status": request.status.value}


@router.post("/{goal_id}/run")
async def run_goal(goal_id: str):
    try:
        return await goal_runner.run(goal_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
