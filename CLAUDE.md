# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running Examples
```bash
# Activate virtual environment first
source .venv/bin/activate

# Basic test example
python -m examples.test

# Research example (requires API keys)
python -m examples.research_example

# Conversational research example
python -m examples.conversational_research_example

# Dialogue example
python -m examples.dialogue_example
```

### Linting and Formatting
```bash
# Format code (using ruff which is included in dependencies)
ruff format src/ examples/

# Lint code
ruff check src/ examples/
```

### Environment Setup
```bash
# Copy environment template
cp .env.template .env

# Required API keys in .env:
# ANTHROPIC_API_KEY=your_key_here
# HONCHO_API_KEY=your_key_here  
# TAVILY_API_KEY=your_key_here
```

## Architecture Overview

This is a multi-agent AI framework built around conversational agents with tool calling capabilities and persistent memory via Honcho.

### Core Components

**Agent System** (`src/agent.py`):
- `Agent`: Main conversational agent with tool execution loop
- `SubAgent`: Lightweight agent for delegation
- Both use streaming responses and memory persistence
- Support up to 50 iterations per conversation

**State Management** (`src/agent_state.py`):
- Integration with Honcho API for persistent conversation memory
- Cross-session knowledge querying and conversation search
- Metadata management for sessions

**Tool System** (`src/tool_registry.py`):
- Decorator-based tool registration with automatic schema generation
- Function signature introspection for parameter validation
- Centralized tool execution with error handling

**LLM Interface** (`src/llm.py`):
- Anthropic Claude API client with streaming support
- Tool calling integration with function schemas
- Async/sync dual interface

### Built-in Tools (`src/tools/`)

- `internet_search`: Tavily-powered web search
- `ls`: List files in `agent_output/` directory
- `read_file`/`write_file`: File operations scoped to `agent_output/`
- All tools use the `@tool` decorator for automatic registration

### Agent Creation Pattern

Use `create_deep_agent()` from `src/main.py` as the entry point:

```python
from src import create_deep_agent
from src.tool_registry import tool
from src.tools import internet_search, ls, read_file, write_file

# Custom tool example
@tool(description="Your tool description")
def my_custom_tool(param: str) -> str:
    return f"Result: {param}"

agent = create_deep_agent(
    name="MyAgent",
    tools=[my_custom_tool, internet_search, ls, read_file, write_file],
    instructions="Your agent instructions here",
    model="claude-4-sonnet-20250514",  # Default model
    verbose=True
)

agent.invoke("Hello!")
```

### Memory and Sessions

- Each agent gets a unique session ID for conversation persistence
- Messages automatically stored in Honcho with peer identification
- Cross-agent knowledge sharing through peer chat functionality
- Session metadata for context preservation

### Key Dependencies

- `honcho-ai`: Conversation memory and agent state management
- `tavily-python`: Internet search capabilities  
- `aiohttp`: Async HTTP client for streaming
- `python-dotenv`: Environment variable management
- `ruff`: Code formatting and linting

## File Structure Context

- `src/`: Core framework code
- `examples/`: Usage examples and patterns
- `agent_output/`: Sandboxed directory for agent file operations
- `.env`: Required API keys (copy from `.env.template`)

## Testing

No formal test suite is present. Test functionality using the example scripts in `examples/`.