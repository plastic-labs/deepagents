import asyncio
import sys
import os
from typing import Literal
from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
sys.path.insert(0, project_root)

from src import create_deep_agent, SubAgent, AgentState

# Load environment variables
load_dotenv()

# Search tool implementation
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    print(f"🔍 Searching: {query}")
    # Mock implementation - replace with actual Tavily client
    return {
        "results": [
            {"title": f"Result for {query}", "content": f"Detailed information about {query}"}
        ]
    }

# Optional: Direct filesystem tool (if you want files saved immediately)
from src.tools import tool

@tool(description="Write content directly to filesystem")
def write_to_filesystem(filename: str, content: str) -> str:
    """Write content directly to a file on the filesystem"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {filename}"
    except Exception as e:
        return f"Error writing to {filename}: {str(e)}"

# Research sub-agent prompt
sub_research_prompt = """You are a dedicated researcher. Your job is to conduct research based on the users questions.

Conduct thorough research and then reply to the user with a detailed answer to their question

only your FINAL answer will be passed on to the user. They will have NO knowledge of anything except your final message, so your final report should be your final message!"""

# Critique sub-agent prompt
sub_critique_prompt = """You are a dedicated editor. You are being tasked to critique a report.

You can find the report at `final_report.md`.

Things to check:
- Check that each section is appropriately named
- Check that the report is comprehensive and detailed
- Check that the article covers key areas and provides valuable insights
- Check that the article has a clear structure and fluent language
- Provide constructive feedback for improvement"""

# Create subagents
research_sub_agent = SubAgent(
    name="research-agent",
    description="Used to research more in depth questions. Only give this researcher one topic at a time.",
    prompt=sub_research_prompt,
    tools=["internet_search"]
)

critique_sub_agent = SubAgent(
    name="critique-agent",
    description="Used to critique the final report and provide feedback.",
    prompt=sub_critique_prompt
)

# Research instructions
research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.

The first thing you should do is to write the original user question to `question.txt` so you have a record of it.

Use the research-agent to conduct deep research. It will respond to your questions/topics with a detailed answer.

When you think you have enough information to write a final report, write it to `final_report.md`.

You can call the critique-agent to get a critique of the final report. After that (if needed) you can do more research and edit the `final_report.md`.

You have two file writing options:
1. Use `write_file` for internal state (files stay in memory)
2. Use `write_to_filesystem` to save files directly to disk immediately

Write a comprehensive report with proper structure, detailed analysis, and source references."""

async def main():
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return
    
    # Create the agent with subagents
    agent = create_deep_agent(
        [internet_search, write_to_filesystem],
        research_instructions,
        subagents=[research_sub_agent, critique_sub_agent]
    )
    
    # Create state
    state = AgentState()
    state.add_message("user", "Research the impact of AI on healthcare in 2024")
    
    print("🤖 Starting deep research agent with subagents...")
    print("This may take a few minutes...")
    
    # Run agent
    result = await agent.invoke(state)
    
    print("\n=== Research Complete ===")
    
    # Save files from agent state to actual filesystem
    for filename, content in result.files.items():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Saved {filename} to filesystem")
        except Exception as e:
            print(f"❌ Failed to save {filename}: {e}")
    
    # Show final state
    if "final_report.md" in result.files:
        print("\n📄 Report Preview:")
        print(result.files["final_report.md"][:500] + "...")
    
    print(f"\n📁 Files created in agent state: {list(result.files.keys())}")
    print(f"✅ Todos completed: {[todo.content for todo in result.todos]}")

if __name__ == "__main__":
    asyncio.run(main())