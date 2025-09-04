import asyncio
import os
import sys
from typing import Literal

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

from src import SubAgent, create_deep_agent  # noqa: E402
from src.tool_registry import tool  # noqa: E402
from src.tools import internet_search, ls, read_file, write_file, complete_task  # noqa: E402

# Load environment variables
load_dotenv()


# Conversational tool for user interaction
@tool(
    description="Communicate with the user - ask questions, provide updates, or share findings"
)
def communicate_with_user(
    message: str,
    message_type: Literal["question", "update", "finding", "info"] = "info",
) -> dict[str, str]:
    """
    Communicate with the user during the research process.

    Args:
        message: The message to send to the user
        message_type: Type of message (question, update, finding, info)

    Returns:
        Dictionary containing user's response
    """
    print(f"🤖 [{message_type.capitalize()}]: {message}")
    print("👤 You: ", end="", flush=True)
    user_response = input().strip()
    return {"user_response": user_response}


# Create specialized research subagents
conversational_researcher = SubAgent(
    name="conversational-researcher",
    description="A research specialist that actively communicates with the user to determine what they want to research",
    tools=[communicate_with_user, complete_task],
    instructions="""You are a conversational research specialist. Your role is to:

1. **Engage with the user** - Ask clarifying questions to understand their research needs
2. **Complete the task** - When you have sufficient information, use complete_task to return results to the parent agent

Your workflow should be:
1. Use communicate_with_user to ask what the user wants to research
2. Continue using communicate_with_user to ask clarifying questions about the research topic
3. Once you have a clear understanding of what the user wants researched, use complete_task with a comprehensive summary

Always be conversational, helpful, and thorough. Think of yourself as a research assistant that the user can talk to throughout the process.

IMPORTANT: When the user confirms they want you to proceed with the research (e.g., "ok", "make the report", "go ahead"), immediately use complete_task with a detailed summary of their research requirements instead of continuing to ask questions.""",
)

report_writer = SubAgent(
    name="report-writer",
    description="Specialized in creating comprehensive research reports",
    tools=[internet_search, ls, write_file, read_file, complete_task],
    instructions="""You are a research report writer. Your job is to:

1. Search the internet for information on the user's topic
2. Compile your findings into a comprehensive response
3. Save your findings to a file using write_file
4. Use complete_task to notify the parent agent when finished

Focus on creating well-structured, professional reports that are easy to read and understand.

Write a comprehensive report to `final_report.md` using write_file based on the research requirements provided by the parent agent.

After writing the report, use complete_task with the file name and a brief summary of what you accomplished.""",
)


async def main():
    agent = create_deep_agent(
        name="Coordinator",
        tools=[],
        instructions="You are a Conversational Research Coordinator. Your role is to coordinate an interactive research experience.",
        subagents=[conversational_researcher, report_writer],
        verbose=True,
    )

    result = agent.invoke(
        "Use the conversational assistant to determine what the user wants to research, then delegate to the report writer to write a report. Once the report is complete, let the user know where to find it."
    )

    print("\n=== Research Complete ===")
    print(f"\033[92mFinal result: {result}\033[0m")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
