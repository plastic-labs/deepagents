from typing import Any

from .agent import Agent, SubAgent
from .tool_registry import tool
from .tools.ls import ls
from .tools.read_file import read_file
from .tools.write_file import write_file


# Built-in tools
@tool(description="Create and manage todos")
def write_todos(todos: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    return {"todos": todos}


def create_deep_agent(
    tools: list[Any],
    instructions: str,
    model: str = "claude-4-sonnet-20250514",
    subagents: list[SubAgent] = None,
    name: str = "DeepAgent",
    verbose: bool = True,
) -> Agent:
    """Create a deep agent with built-in tools and optional subagents."""

    # Collect all tools - use actual functions, not just names
    all_tools = []

    # Add built-in tools
    all_tools.extend(
        [
            write_todos,
            ls,
            read_file,
            write_file,
        ]
    )

    # Add user-provided tools
    all_tools.extend(tools)

    return Agent(
        all_tools, instructions, model, name=name, verbose=verbose, subagents=subagents
    )
