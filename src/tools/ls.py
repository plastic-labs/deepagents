import os

from src.tool_registry import tool


@tool(description="List files in the directory")
def ls() -> list[str]:
    """List files in the working directory"""
    try:
        os.makedirs("agent_output", exist_ok=True)
        return os.listdir("agent_output")
    except Exception as e:
        return f"Error listing files: {str(e)}"
