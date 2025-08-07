import asyncio
import os
import sys

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import AgentState, create_deep_agent  # noqa: E402
from src.tools import tool  # noqa: E402
from src.tools.internet_search import internet_search  # noqa: E402

# Load environment variables
load_dotenv()


@tool(description="Get current date and time")
def get_current_time() -> str:
    """Get the current date and time"""
    from datetime import datetime

    return datetime.now().isoformat()


async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return

    # Create agent with registered tools
    agent = create_deep_agent(
        [internet_search, get_current_time], "You are a helpful research assistant."
    )

    # Create state
    state = AgentState()
    state.add_message(
        "user", "What is the capital of France? Search for current information."
    )

    print("🤖 Starting agent...")

    # Run agent
    result = await agent.invoke(state)

    print("\n=== Final Output ===")
    for msg in result.messages:
        role = msg["role"].upper()
        content = msg["content"]
        print(f"[{role}] {content}")

    print(f"\n📁 Files: {list(result.files.keys())}")
    print(f"✅ Todos: {[todo.content for todo in result.todos]}")


if __name__ == "__main__":
    asyncio.run(main())
