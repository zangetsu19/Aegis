from agents import function_tool

from .config import settings
from .memory import MemoryStore
from .tasks import TaskStore


memory_store = MemoryStore(settings.memory_db_path)
task_store = TaskStore(settings.memory_db_path)


@function_tool
def remember(session_id: str, fact: str) -> str:
    """Persist a useful fact or preference for the current session."""
    memory_store.add(session_id, "memory", fact)
    return f"Remembered: {fact}"


@function_tool
def create_task(session_id: str, title: str, objective: str) -> str:
    """Create a persistent task for later execution or tracking."""
    task_id = task_store.create(session_id, title, objective)
    return f"Created task #{task_id}: {title}"


TOOLS = [remember, create_task]
