# Conversational Research Agent Example

This example demonstrates a ChatGPT/Claude.ai-style conversational research agent that allows for back-and-forth dialogue throughout the research process.

## Features

🗣️ **Interactive Conversation**: The agent can ask clarifying questions and respond to user input  
🔍 **Progressive Research**: Research happens incrementally with user guidance  
📊 **Real-time Updates**: The agent provides progress updates during research  
💾 **Report Generation**: Creates and saves comprehensive research reports  
🤖 **Multi-Agent Coordination**: Uses specialized subagents for different research tasks  

## How It Works

### Core Innovation: `communicate_with_user` Tool
The key innovation is implementing user communication as a **tool call**. This allows the agent to:
- Seamlessly switch between research and conversation
- Ask clarifying questions at any point
- Provide progress updates
- Seek feedback on research direction

### Architecture

```
┌─────────────────────────────────────────┐
│         Research Coordinator            │
│  (Main conversational interface)        │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│           Subagents                     │
├─────────────────────────────────────────┤
│ • conversational-researcher             │
│   - Interactive research with user      │
│ • research-analyst                      │
│   - Deep data analysis                  │
│ • report-writer                         │
│   - Comprehensive report creation       │
└─────────────────────────────────────────┘
```

### Key Tools

- **`communicate_with_user`**: Enables two-way conversation
- **`internet_search`**: Conducts research queries
- **`analyze_research_data`**: Analyzes and extracts insights
- **`save_research_report`**: Creates persistent research documents

## Usage

```bash
cd deepagents
python examples/conversational_research_example.py
```

### Example Conversation Flow

```
🤖 What would you like me to research today?
👤 AI in healthcare

🤖 Great topic! To provide the most relevant research, could you tell me:
   1. Are you interested in current applications or future possibilities?
   2. Any specific healthcare areas (diagnostics, treatment, administration)?
   3. What's your background - healthcare professional, student, or general interest?

👤 I'm a medical student interested in current diagnostic applications

🤖 Perfect! I'll focus on current AI diagnostic tools being used in clinical practice.
   Let me start researching... I'll keep you updated on what I find.

[Agent conducts research and provides updates]

🤖 I've found fascinating applications in radiology and pathology. Here's what I've discovered...
   Would you like me to dive deeper into any particular area?
```

## Technical Implementation

### Maximum Code Reuse
This example **maximizes reuse of existing codebase** while adding minimal new functionality:

**Imported from Existing Codebase:**
- `AgentState`, `SubAgent`, `create_deep_agent` from `src/`
- `tool` decorator from `src.tool_registry`
- Built-in tools: `write_todos`, `invoke_subagent`, `ls`, `read_file`, `write_file`, `edit_file`
- Research tools: `internet_search` from `src.tools.internet_search`, `write_file` from `src.tools.write_file`
- Existing agent and conversation management infrastructure

**New Functionality (Example Only):**
- `communicate_with_user` tool - enables two-way conversation
- `ConversationInterface` class - lightweight user interaction
- `analyze_research_data` tool - simple research analysis
- Conversational coordination prompts and logic

### Conversation State Management
- Maintains conversation history in `AgentState`
- Preserves context across research iterations
- Supports file creation and sharing between subagents

### Error Handling
- Graceful handling of user interruptions (Ctrl+C)
- Transparent communication about limitations
- Fallback options when search results are unavailable

## Extending the Example

### Adding Real Search Integration
Replace the mock `internet_search` function with real APIs:
```python
# Example with Tavily API
def internet_search(query: str, max_results: int = 5):
    from tavily import TavilyClient
    client = TavilyClient(api_key="your-api-key")
    return client.search(query, max_results=max_results)
```

### Web Interface Integration
The `communicate_with_user` tool can be adapted for web interfaces:
```python
# For web apps, replace print/input with WebSocket communication
async def communicate_with_user(message: str, wait_for_response: bool = True):
    await websocket.send({"type": "agent_message", "content": message})
    if wait_for_response:
        response = await websocket.receive()
        return {"user_response": response["content"]}
```

### Custom Research Domains
Create specialized research subagents for specific domains:
```python
medical_researcher = SubAgent(
    name="medical-researcher",
    description="Specialized in medical and healthcare research",
    prompt="You are a medical research specialist...",
    tools=["pubmed_search", "clinical_trials_search", "medical_analysis"]
)
```

## Benefits of This Approach

✅ **Natural User Experience**: Similar to ChatGPT/Claude.ai  
✅ **Extensible Architecture**: Easy to add new research domains  
✅ **Progressive Disclosure**: Information revealed incrementally  
✅ **User-Guided Research**: Direction adjusts based on user interest  
✅ **Persistent Results**: Research can be saved and continued later  

## Requirements

- Python 3.8+
- `anthropic` package for Claude API
- `python-dotenv` for environment variables
- Set `ANTHROPIC_API_KEY` in your `.env` file

---

This example demonstrates how the deepagents framework can be extended to create sophisticated, conversational AI assistants without modifying the core library code.