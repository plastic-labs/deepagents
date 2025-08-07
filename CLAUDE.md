# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

This is a Python project using uv for dependency management (Python 3.12+). Install dependencies with:
```bash
uv sync
```

Run code with:
```bash
uv run python examples/dialogue_example.py
uv run python examples/research_example.py
```

Code quality:
```bash
uv run ruff check   # Lint the codebase
uv run ruff format  # Format code
```

## Architecture Overview

DeepAgents is an AI agent framework built around task orchestration and tool delegation. The core architecture follows this pattern:

### Core Components

- **Agent** (`src/agent.py`): Main agent class with conversation management and tool execution
- **AgentState** (`src/state.py`): Stateful container for messages, files, and todos across agent conversations
- **ToolRegistry** (`src/tools.py`): Decorator-based tool registration system for function calling
- **LLMClient** (`src/llm.py`): Anthropic API wrapper for Claude integration
- **TaskAgent** (`src/main.py`): Multi-agent coordination system with subagent handoffs

### Key Patterns

**Tool Definition**: Use the `@tool` decorator to create callable functions:
```python
from src.tools import tool

@tool(description="Search the internet")
def search_tool(query: str) -> dict:
    return {"results": [...]}
```

**Agent Creation**: Use `create_deep_agent()` factory function:
```python
from src import create_deep_agent, SubAgent

agent = create_deep_agent(
    tools=[search_tool, write_tool],
    instructions="System prompt here",
    subagents=[SubAgent(...)],  # Optional
    verbose=True  # Enable detailed logging
)
```

**SubAgent Pattern**: Create specialized agents for specific tasks:
```python
researcher = SubAgent(
    name="researcher",
    description="Conducts research tasks",
    prompt="You are a research specialist...",
    tools=["internet_search"]  # Tool names as strings
)
```

**State Management**: Files and conversations persist in AgentState:
- `state.files` - In-memory file system
- `state.messages` - Conversation history
- `state.todos` - Task tracking

### Multi-Agent Coordination

The framework supports hierarchical agent delegation:
1. Main agent receives user task
2. Delegates subtasks to specialized subagents via `invoke_subagent` tool
3. SubAgents complete tasks and return results
4. Main agent synthesizes final response

Built-in tools available to all agents:
- `write_todos` - Task management
- `invoke_subagent` - Agent delegation
- `ls`, `read_file`, `write_file`, `edit_file` - File operations

## Environment Variables

Required in `.env` file:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Examples

- `examples/dialogue_example.py` - Multi-agent coordination demo
- `examples/research_example.py` - Research workflow with subagents

Both examples show the enhanced logging system that tracks agent conversations and tool usage in detail.