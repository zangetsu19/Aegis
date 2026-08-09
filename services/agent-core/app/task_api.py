from .tasks import TaskStore
from .config import settings


task_store = TaskStore(settings.memory_db_path)


def list_tasks(session_id: str) -> list[dict]:
    return task_store.list(session_id)
