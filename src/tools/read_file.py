from src.tool_registry import tool


@tool(description="Read file contents")
def read_file(filename: str) -> str:
    """Read file contents"""
    with open(f"agent_output/{filename}", "r", encoding="utf-8") as f:
        content = f.read()
    return content
