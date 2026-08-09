from fastapi import APIRouter

from .config import settings
from .skill_learning import SkillLearner, SkillStore

router = APIRouter(prefix="/v1/skills", tags=["skills"])
store = SkillStore(settings.memory_db_path)
learner = SkillLearner(store)


@router.get("/{session_id}")
async def skills(session_id: str):
    return {"session_id": session_id, "skills": store.list(session_id)}
