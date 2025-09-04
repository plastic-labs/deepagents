import asyncio
import os
import sys

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import SubAgent, create_deep_agent  # noqa: E402
from src.tools import internet_search, ls, read_file, write_file  # noqa: E402

# Load environment variables
load_dotenv()


async def main():
    # Create a subagent
    subagent = SubAgent(
        name="Junior_Research_Agent",
        description="A subagent that can gather information from the internet. You should delegate to this subagent when you need to gather information.",
        tools=[internet_search],
        instructions="You are a helpful research assistant. You have access to the internet and can gather information.",
    )

    # Create agent with registered tools
    agent = create_deep_agent(
        "Senior_Researcher",
        [ls, read_file, write_file],
        "You are a lead researcher. You should delegate to the Junior Research Agent when you need to gather information.",
        subagents=[subagent],
    )

    print("Starting agent...")

    # Run agent
    result = agent.invoke(
        "Who is the current president of the United States? Check the news for the latest information."
    )
    print(f"\033[92mFinal result: {result}\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
