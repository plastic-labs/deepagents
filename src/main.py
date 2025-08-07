from typing import Any

from .agent import Agent
from .state import AgentState
from .tool_registry import tool
from .tools.ls import ls
from .tools.read_file import read_file
from .tools.write_file import write_file


# Built-in tools
@tool(description="Create and manage todos")
def write_todos(todos: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    return {"todos": todos}


@tool(description="Invoke a specialized subagent to handle specific tasks")
def invoke_subagent(
    subagent_type: str, task_description: str, state=None
) -> dict[str, str]:
    """Invoke a specialized subagent with a specific task"""
    # This tool will be enhanced when subagents are available
    # For now, it's a placeholder that gets replaced in actual implementations
    return {
        "message": f"Subagent {subagent_type} invoked with task: {task_description}"
    }


# Subagent support
class SubAgent:
    def __init__(
        self, name: str, description: str, prompt: str, tools: list[str] = None
    ):
        self.name = name
        self.description = description
        self.prompt = prompt
        self.tools = tools or []


class TaskAgent:
    def __init__(
        self,
        tools: list[str],
        instructions: str,
        subagents: list[SubAgent],
        verbose: bool = True,
    ):
        self.agents = {}
        self.verbose = verbose
        self.setup_agents(tools, instructions, subagents)

    def setup_agents(
        self, tools: list[str], instructions: str, subagents: list[SubAgent]
    ):
        # General purpose agent
        self.agents["general-purpose"] = Agent(
            tools, instructions, name="MainAgent", verbose=self.verbose
        )

        # Custom subagents
        for subagent in subagents:
            agent_tools = subagent.tools if subagent.tools else tools
            self.agents[subagent.name] = Agent(
                agent_tools, subagent.prompt, name=subagent.name, verbose=self.verbose
            )

    async def invoke(
        self, description: str, subagent_type: str, state: AgentState
    ) -> AgentState:
        if subagent_type not in self.agents:
            if self.verbose:
                print(f"❌ [TaskAgent] Error: Unknown agent type '{subagent_type}'")
            state.add_message("system", f"Error: Unknown agent type {subagent_type}")
            return state

        if self.verbose:
            print(f"\n🔄 [TaskAgent] Handing off to '{subagent_type}' subagent")
            print(
                f"📝 [TaskAgent] Task description: {description[:100]}{'...' if len(description) > 100 else ''}"
            )

        agent = self.agents[subagent_type]
        new_state = AgentState()
        new_state.messages = [{"role": "user", "content": description}]
        new_state.files = state.files.copy()

        if self.verbose:
            print(f"📁 [TaskAgent] Sharing {len(state.files)} files with subagent")
            if state.files:
                print(f"📁 [TaskAgent] Files: {list(state.files.keys())}")

        result = await agent.invoke(new_state)

        # Merge results
        state.files = result.files
        state.messages.extend(result.messages)

        if self.verbose:
            new_files = (
                set(result.files.keys()) - set(state.files.keys())
                if hasattr(state, "files")
                else set(result.files.keys())
            )
            if new_files:
                print(
                    f"📁 [TaskAgent] Subagent created {len(new_files)} new files: {list(new_files)}"
                )
            print(f"✅ [TaskAgent] Handoff to '{subagent_type}' completed\n")

        return state


def create_deep_agent(
    tools: list[Any],
    instructions: str,
    model: str = "claude-3-5-haiku-20241022",
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
            invoke_subagent,
            ls,
            read_file,
            write_file,
        ]
    )

    # Add user-provided tools
    all_tools.extend(tools)

    return Agent(all_tools, instructions, model, name=name, verbose=verbose)
