# DeepAgents

A sophisticated multi-agent system implementation that leverages **Honcho** as its memory layer to create personalized, learning workflows that adapt to users over time.

## 🧠 What is DeepAgents?

DeepAgents is an implementation of a multi-agent system where agents can collaborate, delegate tasks to specialized subagents, and maintain persistent memory across conversations. The system is designed to learn about users and their preferences over time, enabling increasingly personalized and efficient workflows.

## 🔑 Key Features

### **Persistent Memory with Honcho**
- **Conversation Memory**: Every interaction is stored and retrievable across sessions
- **User Learning**: Agents build knowledge representations of users and their preferences
- **Context Awareness**: Full conversation history available for context-aware responses
- **Search Capabilities**: Semantic search through past conversations and knowledge

### **Multi-Agent Architecture**
- **Coordinator Agents**: Main agents that orchestrate complex workflows
- **Specialized Subagents**: Task-specific agents with focused capabilities
- **Dynamic Delegation**: Agents can invoke subagents based on task requirements
- **Tool Integration**: Rich set of built-in tools for various tasks

### **Built-in Tools**
- `internet_search`: Web search capabilities for research tasks
- `read_file` / `write_file`: File system operations
- `ls`: Directory listing and exploration
- `invoke_subagent`: Delegation to specialized agents
- `complete_task`: Task completion signaling
- `communicate_with_user`: Interactive user communication

## 🏗️ Architecture

### Core Components

1. **Agent Class**: Main agent implementation with tool execution and conversation management
2. **SubAgent Class**: Specialized agents for specific task domains
3. **AgentState**: Honcho-powered state management for persistence and memory
4. **Tool Registry**: Centralized tool management and execution
5. **LLM Client**: Anthropic Claude integration for reasoning

### Memory Layer (Honcho)

The system uses **Honcho** as its memory backbone:

```python
class AgentState:
    def __init__(self, peer_id: str, session_id: str):
        self.honcho = Honcho(environment="production", workspace_id="deepagents-stream-5")
        self.peer = self.honcho.peer(peer_id, config={"observe_me": False})
        self.session = self.honcho.session(session_id, config={"deriver_disabled": True})
```

**Key Memory Features:**
- **Peer Representations**: Each agent maintains a persistent identity
- **Session Management**: Conversation threads are preserved across interactions
- **Knowledge Querying**: Agents can query their accumulated knowledge
- **Conversation Search**: Semantic search through past interactions

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Honcho API access
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd deepagents

# Install dependencies
pip install -e .
```

### Environment Setup

Create a `.env` file with your API keys:

```bash
ANTHROPIC_API_KEY=your_claude_api_key
TAVILY_API_KEY=your_tavily_api_key  # For internet search
```

### Basic Usage

```python
from src import create_deep_agent, SubAgent

# Create a specialized subagent
researcher = SubAgent(
    name="researcher",
    description="Specialized in gathering and analyzing information",
    tools=[internet_search, read_file, write_file],
    instructions="You are a research specialist..."
)

# Create the main agent
agent = create_deep_agent(
    name="Coordinator",
    tools=[],
    instructions="Coordinate research workflows and delegate tasks appropriately",
    subagents=[researcher],
    verbose=True
)

# Start the conversation
result = await agent.invoke("Research the latest developments in AI")
```

## 📚 Examples

### Conversational Research Example

The `conversational_research_example.py` demonstrates how agents can:

1. **Engage in dialogue** with users to understand requirements
2. **Delegate research tasks** to specialized subagents
3. **Maintain context** across the entire workflow
4. **Learn user preferences** for future interactions

### Research Workflow Example

The `research_example.py` shows a complete research pipeline:

1. **Task Analysis**: Understanding research requirements
2. **Information Gathering**: Web search and data collection
3. **Report Generation**: Structured output creation
4. **Memory Storage**: All interactions saved for future reference

## 🔄 How It Learns Over Time

### Persistent User Knowledge

Every interaction contributes to the agent's understanding of the user:

- **Conversation Patterns**: How users prefer to communicate
- **Task Preferences**: What types of tasks users commonly request
- **Workflow Patterns**: How users like to structure their work
- **Feedback Integration**: Learning from user responses and corrections

### Adaptive Workflows

The system becomes more efficient over time:

- **Faster Task Understanding**: Agents recognize common request patterns
- **Better Delegation**: Improved subagent selection based on user history
- **Personalized Responses**: Tailored communication style and detail level
- **Proactive Suggestions**: Anticipating user needs based on past interactions

## 🛠️ Customization

### Creating Custom Subagents

```python
custom_agent = SubAgent(
    name="my-specialist",
    description="Description of what this agent does",
    tools=[your_custom_tools],
    instructions="Detailed instructions for the agent's behavior"
)
```

### Adding Custom Tools

```python
from src.tool_registry import tool

@tool(description="What your tool does")
def my_custom_tool(param1: str, param2: int) -> dict:
    # Tool implementation
    return {"result": "success"}
```

### Extending Agent Capabilities

The modular architecture allows for easy extension:

- **New Tool Types**: Add domain-specific capabilities
- **Custom Memory Strategies**: Implement specialized memory patterns
- **Integration Points**: Connect with external systems and APIs

## 🔍 Advanced Features

### Memory Queries

```python
# Query agent knowledge
knowledge = agent.state.query_agent_knowledge("What does the user prefer for research topics?")

# Search conversations
results = agent.state.search_conversation("machine learning")
```

### Session Management

```python
# Set session metadata
agent.state.set_session_metadata({"project": "AI Research", "priority": "high"})

# Retrieve conversation context
messages = agent.state.get_messages()
```

## 🤝 Contributing

This is an open-source implementation of the DeepAgents concept. Contributions are welcome:

1. **Bug Reports**: Open issues for any problems you encounter
2. **Feature Requests**: Suggest new capabilities or improvements
3. **Code Contributions**: Submit pull requests for enhancements
4. **Documentation**: Help improve examples and documentation

## 🙏 Acknowledgments

- **Honcho**: For providing the powerful memory and knowledge management layer
- **Anthropic**: For Claude AI capabilities
- **Open Source Community**: For the tools and libraries that make this possible

---

**DeepAgents**: Where AI agents learn, remember, and grow with you over time.
