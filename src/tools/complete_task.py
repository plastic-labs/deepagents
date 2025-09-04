from src.tool_registry import tool


@tool(description="Deliver final result to user")
def complete_task(result: str):
    """NOTE: fake tool handled by agent loop"""
    return
