from agents import function_tool


@function_tool
def remember(session_id: str, fact: str) -> str:
    """Record a durable user/project fact for the current session."""
    # The runtime injects the real persistence implementation later.
    return f"Memory candidate recorded for session {session_id}: {fact}"


@function_tool
def create_task(title: str, objective: str) -> str:
    """Create a task proposal for the AEGIS task engine."""
    return f"Task proposal created: {title} — {objective}"


TOOLS = [remember, create_task]
