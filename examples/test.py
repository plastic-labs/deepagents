import asyncio
import os
import sys

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import AgentState, create_deep_agent  # noqa: E402
from src.tools.internet_search import internet_search  # noqa: E402

# Load environment variables
_ = load_dotenv()


async def main():
    # Check for API keys
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return

    # Create agent with enhanced dialogue logging
    agent = create_deep_agent(
        [internet_search],
        "You are a helpful research assistant.",
        name="ResearchAssistant",
        verbose=True,  # Enable enhanced dialogue logging
    )

    # Create state
    state = AgentState()
    state.add_message("user", "What is the capital of France?")

    # Run agent
    result = await agent.invoke(state)

    print("Messages:", result.messages)
    print("Files:", result.files)
    print("Todos:", [todo.content for todo in result.todos])


if __name__ == "__main__":
    asyncio.run(main())
