import asyncio
import uuid
import os
import sys
from typing import Literal
from honcho import Honcho

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

# Import existing functionality from the codebase
from src import SubAgent  # noqa: E402
from src.agent import Agent  # noqa: E402
from src.tool_registry import tool  # noqa: E402

# Import existing research tools
from src.tools.internet_search import internet_search  # noqa: E402
from src.tools.ls import ls
from src.tools.read_file import read_file
from src.tools.write_file import write_file

# Load environment variables
_ = load_dotenv()

session_id = str(uuid.uuid4())


# Simple conversation manager for user interface (new functionality only)
@tool(description="Invoke a specialized subagent to handle specific tasks")
def invoke_subagent(subagent_type: str, task_description: str) -> dict[str, str]:
    """Invoke a specialized subagent with a specific task"""
    subagent_dict = {
        "conversational-researcher": conversational_researcher,
        "report-writer": report_writer,
    }
    subagent = subagent_dict[subagent_type]
    agent = Agent(
        tools=subagent.tools,
        instructions=subagent.prompt + f"\n\nTask: {task_description}",
        name=subagent_type,
        verbose=True,
        session_id=session_id,
    )
    agent.invoke()


# NEW FUNCTIONALITY: Conversational tool for user interaction
@tool(
    description="Communicate with the user - ask questions, provide updates, or share findings"
)
def communicate_with_user(
    message: str,
    message_type: Literal["question", "update", "finding", "info"] = "info",
    # wait_for_response: bool = True,
) -> dict[str, str]:
    """
    Communicate with the user during the research process.

    Args:
        message: The message to send to the user
        message_type: Type of message (question, update, finding, info)
        wait_for_response: Whether to wait for user response (False for status updates)

    Returns:
        Dictionary containing user's response if wait_for_response=True
    """
    print("🤖 " + message)
    print("👤 You: ", end="", flush=True)
    user_response = input().strip()
    return {"user_response": user_response}


# Create specialized research subagents using existing + new tools
conversational_researcher = SubAgent(
    name="conversational-researcher",
    description="A research specialist that actively communicates with the user throughout the research process",
    prompt="""You are a conversational research specialist. Your role is to:

1. **Engage with the user** - Ask clarifying questions to understand their research needs
2. **Provide research progress updates** - Keep the user informed about what you're discovering  
3. **Present findings interactively** - Share key insights and ask if they want more detail
4. **Adapt based on feedback** - Adjust research direction based on user input

Your workflow should be:
1. Ask clarifying questions about the research topic using communicate_with_user
2. Provide periodic updates as you research using communicate_with_user with wait_for_response=False
3. Present key findings and ask if the user wants to explore specific areas deeper
4. Continue the conversation based on user interests and questions

Always be conversational, helpful, and thorough. Think of yourself as a research assistant that the user can talk to throughout the process.""",
    tools=[communicate_with_user, internet_search],
)

report_writer = SubAgent(
    name="report-writer",
    description="Specialized in creating comprehensive research reports",
    prompt="""You are a research report writer. Your job is to:

1. Compile research findings into comprehensive reports  
2. Structure information clearly and logically
3. Include executive summaries and detailed sections
4. Save reports using write_file for persistent storage

Focus on creating well-structured, professional reports that are easy to read and understand.

When you think you have enough information to write a final report, write it to `final_report.md` using write_file.""",
    tools=[
        write_file,
        communicate_with_user,
        ls,
        read_file,
    ],  # Use existing file tools
)

# Main conversational research coordinator
research_coordinator_instructions = """You are a Conversational Research Coordinator. Your role is to facilitate an interactive research experience similar to ChatGPT or Claude.ai.

Available subagents:
1. 'conversational-researcher' - For conducting interactive research with user engagement
3. 'report-writer' - For creating comprehensive research reports

Your approach should be:

1. **Start with engagement** - Welcome the user and understand what they want to research
2. **Use conversational-researcher** - This subagent will handle the interactive research process
3. **Provide reports** - Use report-writer when the user wants formal documentation

Key principles:
- Always use communicate_with_user to interact with the user
- Be conversational and friendly
- Provide value at each step
- Ask for clarification when needed
- Allow the conversation to flow naturally
- The conversation should continue until a report is written by the report-writer subagent

Remember: This is a conversation, not just a one-time task. The user may ask follow-up questions, request different research directions, or want to dive deeper into specific areas.

You must invoke sub-agents to complete the research process.

You need to invoke a sub-agent or the process will end and you will die. invoke subagents to stay alive.
"""


def main():
    """Main function to run the conversational research agent"""
    honcho_client = Honcho(environment="production", workspace_id="deepagents")

    honcho_client.peer("tool-caller", config={"observe_me": False})

    # Collect all tools - use actual functions, not just names
    tools = [
        # communicate_with_user,
        # internet_search,
        invoke_subagent,
        # ls,
        # read_file,
        # write_file,
    ]

    # Add user-provided tools
    agent = Agent(
        tools=tools,
        instructions=research_coordinator_instructions,
        subagents=[conversational_researcher, report_writer],
        name="ResearchCoordinator",
        verbose=True,
        session_id=session_id,
    )

    agent.invoke()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
