import asyncio
import os
import sys

from dotenv import load_dotenv
from eth_account import Account

from x402.clients.httpx import x402HttpxClient

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import create_deep_agent  # noqa: E402
from src.tool_registry import tool  # noqa: E402
from src.tools import ls, read_file, write_file  # noqa: E402

# Load environment variables
load_dotenv()

account = Account.from_key(os.getenv("WALLET_PRIVATE_KEY"))


@tool(description="Pay for expert advice")
async def query_tech_expert(question: str) -> str:
    """
    Asynchronously query the expert API with a URL-encoded question.

    Args:
        question: The question string to send to the expert.

    Returns:
        The response text from the expert API.
    """
    from urllib.parse import quote_plus

    encoded_question = quote_plus(question)
    print(f"Encoded question: {encoded_question}")
    async with x402HttpxClient(
        account=account,
        base_url="https://www.x402.org",  # TODO: penny for your thoughts!
    ) as client:
        response = await client.get("/protected")
        print(await response.aread())
    return "lol"


async def main():
    # Create agent with registered tools
    agent = create_deep_agent(
        "Researcher",
        [query_tech_expert, ls, read_file, write_file],
        "You are a helpful research assistant. You may query an expert for advice.",
    )

    print("Starting agent...")

    # Run agent
    result = await agent.invoke(
        "Give me an expert perspective on the ideal team size for a technical team."
    )
    print(f"\033[92mFinal result: {result}\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
