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

# Research sub-agent instructions
research_instructions = """You are a dedicated researcher. Your job is to conduct thorough research based on the user's questions.

Process:
1. Use internet_search to gather information on the requested topic
2. Search for multiple aspects: key developments, statistics, real-world examples, challenges
3. Compile your findings into a comprehensive response

Your final response should include:
- Key developments and breakthroughs
- Market data and statistics
- Real-world case studies and examples
- Current challenges and solutions
- Future trends and implications

Be thorough but efficient - conduct 3-5 targeted searches to gather comprehensive information."""

# Critique sub-agent instructions
critique_instructions = """You are a professional report editor and critic.

Process:
1. Use read_file to examine the report that needs review
2. Evaluate the report across multiple dimensions
3. Provide structured feedback with specific recommendations

Evaluation criteria:
- Structure and organization
- Comprehensiveness and depth of coverage  
- Use of data and evidence
- Clarity and readability
- Professional quality
- Areas for improvement

Provide a clear, actionable critique with specific suggestions for enhancement."""

# Create subagents
research_subagent = SubAgent(
    name="research-agent",
    description="Used to research in-depth questions. Only give this researcher one topic at a time.",
    tools=[internet_search],
    instructions=research_instructions,
)

critique_subagent = SubAgent(
    name="critique-agent",
    description="Used to critique reports and provide feedback.",
    tools=[read_file, ls],
    instructions=critique_instructions,
)

# Main research coordinator instructions
research_coordinator_instructions = """You are an expert research coordinator. Your job is to conduct thorough research and write polished reports.

Your workflow should be:

1. Save the original user question to `question.txt` using write_file (do this only once)
2. Use the research-agent subagent to conduct deep research on the topic
3. Write a comprehensive report to `final_report.md` based on the research findings
4. Optionally use the critique-agent to review your report and provide feedback
5. When you have completed the research and written the report, use complete_task to provide the final result

Important guidelines:
- Only save the question once at the beginning
- Focus on producing a single, high-quality comprehensive report
- Use the research findings to create detailed, well-structured content
- Don't repeat the same actions multiple times

Available tools:
- invoke_subagent: Delegate research and critique tasks to specialized agents
- write_file: Save files (filename, content) - use sparingly and purposefully
- read_file: Read existing files when needed
- ls: List files in the output directory
- complete_task: Signal completion and provide final result"""


async def main():
    agent = create_deep_agent(
        name="ResearchCoordinator",
        tools=[ls, read_file, write_file],
        instructions=research_coordinator_instructions,
        subagents=[research_subagent, critique_subagent],
        verbose=True,
    )

    print("🤖 Starting deep research agent with subagents...")
    print("This may take a few minutes...")

    # Run agent
    result = agent.invoke("Research the impact of AI on healthcare in 2024")

    print("\n=== Research Complete ===")
    print(f"\033[92mFinal result: {result}\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
