import asyncio
import os
import sys
import uuid

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import AgentState, create_deep_agent  # noqa: E402
from src.tool_registry import tool  # noqa: E402
from src.tools.internet_search import internet_search  # noqa: E402

# Load environment variables
_ = load_dotenv()

state = AgentState(session_id=f"test-{uuid.uuid4()}")


@tool(description="Query user's representation")
def honcho_chat(query: str) -> str:
    """Query the user's representation"""
    return state.query_user_knowledge(query)


async def main():
    # Check for API keys
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return

    # Create agent with enhanced dialogue logging
    agent = create_deep_agent(
        [internet_search, honcho_chat],
        "You are a helpful research assistant. Before answering the user's research question, you must query the user's representation using `honcho_chat` to get more information.",
        name="ResearchAssistant",
        verbose=True,  # Enable enhanced dialogue logging
    )

    # Create state
    state.add_message("user", "What is the capital of France?")

    # Run agent
    result = await agent.invoke(state)

    print("Messages:", result.get_messages())
    print("Todos:", result.get_todos())


if __name__ == "__main__":
    asyncio.run(main())
