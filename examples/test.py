import asyncio
import sys
import os
from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
sys.path.insert(0, project_root)

from src import create_deep_agent, AgentState

# Load environment variables
load_dotenv()

# Example usage
def internet_search(query: str) -> dict:
    """Search the internet"""
    return {"results": [f"Found results for {query}"]}

async def main():
    # Check for API keys
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return
    
    # Create agent
    agent = create_deep_agent(
        [internet_search],
        "You are a helpful research assistant."
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