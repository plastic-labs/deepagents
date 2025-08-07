import asyncio
import os
import sys

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import AgentState, SubAgent, create_deep_agent  # noqa: E402
from src.tool_registry import tool  # noqa: E402
from src.tools.internet_search import internet_search  # noqa: E402

# Load environment variables
_ = load_dotenv()


@tool(description="Analyze data and provide insights")
def data_analysis(data: str) -> dict[str, str]:
    """Analyze provided data"""
    print(f"📊 [Tool] Analyzing data: {data[:50]}{'...' if len(data) > 50 else ''}")
    return {"analysis": f"Analysis of {data}: Key insights and patterns found"}


# Create specialized subagents
researcher = SubAgent(
    name="researcher",
    description="Specialized agent for conducting research and gathering information",
    prompt="""You are a research specialist. Your job is to:
1. Search for relevant information using available tools
2. Analyze and synthesize the information
3. Provide comprehensive research summaries
4. Focus on accuracy and thoroughness

When given a research task, break it down into specific search queries and gather comprehensive information.""",
    tools=["internet_search"],
)

analyst = SubAgent(
    name="analyst",
    description="Specialized agent for data analysis and insights",
    prompt="""You are a data analysis specialist. Your job is to:
1. Examine provided data or research
2. Identify patterns and insights
3. Draw meaningful conclusions
4. Present findings clearly

Focus on providing actionable insights and clear explanations of your analysis.""",
    tools=["data_analysis"],
)

writer = SubAgent(
    name="writer",
    description="Specialized agent for creating polished written content",
    prompt="""You are a professional writer. Your job is to:
1. Create well-structured, engaging content
2. Ensure clarity and readability
3. Adapt tone and style to the audience
4. Save final content to files when appropriate

Focus on creating high-quality, polished written work.""",
    tools=["write_to_filesystem"],
)

# Main coordinator instructions
coordinator_instructions = """You are the Coordinator Agent. Your role is to orchestrate multiple specialized subagents to complete complex tasks.

Available subagents:
1. 'researcher' - For gathering information and conducting research
2. 'analyst' - For analyzing data and providing insights  
3. 'writer' - For creating polished written content

Your workflow should be:
1. Break down the user's request into subtasks
2. Delegate appropriate tasks to specialized subagents using invoke_subagent
3. Coordinate the work between subagents
4. Synthesize the final results

Always explain your thinking process and which subagent you're using for each task."""


async def main():
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return

    print("🚀 Enhanced DeepAgents Dialogue Example")
    print("=" * 50)

    # Create the main coordinator agent
    coordinator = create_deep_agent(
        tools=[internet_search, data_analysis],
        instructions=coordinator_instructions,
        subagents=[researcher, analyst, writer],
        name="Coordinator",
        verbose=True,  # Enable detailed logging
    )

    # Create initial state
    state = AgentState()

    # Example complex task
    task = """Research the benefits of meditation for productivity, analyze the key findings, 
    and write a comprehensive report with practical recommendations."""

    state.add_message("user", task)

    print(f"📋 Task: {task}")
    print("\n" + "=" * 50)
    print("🎭 AGENT DIALOGUE LOG")
    print("=" * 50)

    # Run the coordinator
    result = await coordinator.invoke(state)

    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)

    # Show conversation summary
    print(f"\n💬 Total conversation turns: {len(result.messages)}")
    print(
        f"📝 Final message count: {len([m for m in result.messages if m['role'] == 'assistant'])}"
    )

    if result.todos:
        print(f"✅ Todos: {[todo.content for todo in result.todos]}")


async def simple_example():
    """Simpler example showing just the enhanced logging"""
    print("\n🔧 Simple Agent Dialogue Example")
    print("=" * 40)

    # Create a simple agent with enhanced logging
    simple_agent = create_deep_agent(
        tools=[internet_search],
        instructions="You are a helpful assistant. Use the available tools to help answer questions.",
        name="Helper",
        verbose=True,
    )

    state = AgentState()
    state.add_message("user", "What are the key benefits of exercise?")

    result = await simple_agent.invoke(state)

    print("result", result)

    print("\n✅ Simple example completed!")


if __name__ == "__main__":
    print("Choose an example:")
    print("1. Complex multi-agent dialogue (default)")
    print("2. Simple enhanced logging example")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "2":
        asyncio.run(simple_example())
    else:
        asyncio.run(main())
