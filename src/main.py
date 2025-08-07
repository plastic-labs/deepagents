from .state import AgentState
from .tools import tool
from .agent import Agent
from typing import List, Any, Dict


# Built-in tools
@tool(description="Create and manage todos")
def write_todos(todos: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    return {"todos": todos}


@tool(description="Invoke a specialized subagent to handle specific tasks")
def invoke_subagent(subagent_type: str, task_description: str, state=None) -> Dict[str, str]:
    """Invoke a specialized subagent with a specific task"""
    # This tool will be enhanced when subagents are available
    # For now, it's a placeholder that gets replaced in actual implementations
    return {"message": f"Subagent {subagent_type} invoked with task: {task_description}"}


@tool(description="List all files")
def ls(state) -> List[str]:
    return list(state.files.keys())


@tool(description="Read file contents")
def read_file(file_path: str, offset: int = 0, limit: int = 2000, state=None) -> str:
    if file_path not in state.files:
        return f"Error: File '{file_path}' not found"

    content = state.files[file_path]
    lines = content.splitlines()

    start_idx = offset
    end_idx = min(start_idx + limit, len(lines))

    if start_idx >= len(lines):
        return f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)"

    result_lines = []
    for i in range(start_idx, end_idx):
        result_lines.append(f"{i + 1:6d}\t{lines[i]}")

    return "\n".join(result_lines)


@tool(description="Write to a file")
def write_file(file_path: str, content: str, state=None) -> Dict[str, Dict[str, str]]:
    state.files[file_path] = content
    return {"files": state.files}


@tool(description="Edit file contents")
def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
    state=None,
) -> Dict[str, Dict[str, str]]:
    if file_path not in state.files:
        return f"Error: File '{file_path}' not found"

    content = state.files[file_path]

    if not replace_all:
        occurrences = content.count(old_string)
        if occurrences > 1:
            return f"Error: String appears {occurrences} times. Use replace_all=True or provide more context"

    new_content = (
        content.replace(old_string, new_string)
        if replace_all
        else content.replace(old_string, new_string, 1)
    )
    state.files[file_path] = new_content
    return {"files": state.files}


# Subagent support
class SubAgent:
    def __init__(
        self, name: str, description: str, prompt: str, tools: List[str] = None
    ):
        self.name = name
        self.description = description
        self.prompt = prompt
        self.tools = tools or []


class TaskAgent:
    def __init__(self, tools: List[str], instructions: str, subagents: List[SubAgent], verbose: bool = True):
        self.agents = {}
        self.verbose = verbose
        self.setup_agents(tools, instructions, subagents)

    def setup_agents(
        self, tools: List[str], instructions: str, subagents: List[SubAgent]
    ):
        # General purpose agent
        self.agents["general-purpose"] = Agent(tools, instructions, name="MainAgent", verbose=self.verbose)

        # Custom subagents
        for subagent in subagents:
            agent_tools = subagent.tools if subagent.tools else tools
            self.agents[subagent.name] = Agent(agent_tools, subagent.prompt, name=subagent.name, verbose=self.verbose)

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
            print(f"📝 [TaskAgent] Task description: {description[:100]}{'...' if len(description) > 100 else ''}")

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
            new_files = set(result.files.keys()) - set(state.files.keys()) if hasattr(state, 'files') else set(result.files.keys())
            if new_files:
                print(f"📁 [TaskAgent] Subagent created {len(new_files)} new files: {list(new_files)}")
            print(f"✅ [TaskAgent] Handoff to '{subagent_type}' completed\n")
        
        return state


def create_deep_agent(
    tools: List[Any],
    instructions: str,
    model: str = "claude-3-5-haiku-20241022",
    subagents: List[SubAgent] = None,
    name: str = "DeepAgent",
    verbose: bool = True,
) -> Agent:
    """Create a deep agent with built-in tools and optional subagents."""

    # Collect all tools - use actual functions, not just names
    all_tools = []
    
    # Add built-in tools
    all_tools.extend([write_todos, invoke_subagent, ls, read_file, write_file, edit_file])
    
    # Add user-provided tools
    all_tools.extend(tools)
    
    return Agent(all_tools, instructions, model, name=name, verbose=verbose)

