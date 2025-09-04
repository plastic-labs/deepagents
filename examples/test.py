import asyncio
import os
import sys

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import create_deep_agent  # noqa: E402
from src.tool_registry import tool  # noqa: E402
from src.tools import internet_search, ls, read_file, write_file  # noqa: E402

# Load environment variables
load_dotenv()


@tool(description="Get current date and time")
def get_current_time() -> str:
    """Get the current date and time"""
    from datetime import datetime

    return datetime.now().isoformat()


async def main():
    # Create agent with registered tools
    agent = create_deep_agent(
        "Researcher",
        [get_current_time, internet_search, ls, read_file, write_file],
        "You are a helpful research assistant.",
    )

    print("Starting agent...")

    # Run agent
    result = agent.invoke("What is the current time?")
    print(f"\033[92mFinal result: {result}\033[0m")

    # Run agent again
    result = agent.invoke(
        "Who is the current president of France? Check the news for the latest information."
    )
    print(f"\033[92mFinal result: {result}\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
