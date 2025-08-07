import os

from src.tool_registry import tool


@tool(description="Write content directly to filesystem")
def write_file(filename: str, content: str) -> str:
    """Write content directly to a file on the filesystem"""
    try:
        os.makedirs("agent_output", exist_ok=True)
        with open(f"agent_output/{filename}", "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {filename}"
    except Exception as e:
        return f"Error writing to {filename}: {str(e)}"
