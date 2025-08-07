import os

from src.tool_registry import tool


def prepend(file_path: str) -> str:
    return f"agent_output/{file_path}"


@tool(description="Write content directly to filesystem")
def write_file(filename: str, content: str) -> str:
    """Write content directly to a file on the filesystem"""
    try:
        os.makedirs("agent_output", exist_ok=True)
        with open(prepend(filename), "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {filename}"
    except Exception as e:
        return f"Error writing to {filename}: {str(e)}"
