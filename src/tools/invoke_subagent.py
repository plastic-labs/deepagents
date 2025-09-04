from src.tool_registry import tool


@tool(description="Invoke a subagent")
def invoke_subagent(subagent_name: str, prompt: str) -> str:
    """NOTE: fake tool handled by agent loop"""
    return ""
