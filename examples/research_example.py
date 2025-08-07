import asyncio
import os
import sys

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import AgentState, SubAgent, create_deep_agent  # noqa: E402
from src.tools.internet_search import internet_search  # noqa: E402

# Load environment variables
load_dotenv()

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
    tools=["internet_search"],
)

critique_sub_agent = SubAgent(
    name="critique-agent",
    description="Used to critique the final report and provide feedback.",
    prompt=sub_critique_prompt,
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

    # Create the agent with subagents and enhanced dialogue logging
    agent = create_deep_agent(
        [internet_search],
        research_instructions,
        subagents=[research_sub_agent, critique_sub_agent],
        name="ResearchCoordinator",
        verbose=True,  # Enable enhanced dialogue logging
    )

    # Create state
    state = AgentState()
    state.add_message("user", "Research the impact of AI on healthcare in 2024")

    print("🤖 Starting deep research agent with subagents...")
    print("This may take a few minutes...")

    # Run agent
    result = await agent.invoke(state)

    print("\n=== Research Complete ===")

    print(f"✅ Todos completed: {[todo.content for todo in result.todos]}")


if __name__ == "__main__":
    asyncio.run(main())
