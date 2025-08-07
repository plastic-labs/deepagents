from src.tool_registry import tool


def prepend(file_path: str) -> str:
    return f"agent_output/{file_path}"


@tool(description="Read file contents")
def read_file(file_path: str) -> str:
    """Read file contents"""
    with open(prepend(file_path), "r", encoding="utf-8") as f:
        content = f.read()
    return content
