import asyncio
import os
import sys
from typing import Literal, Optional

from dotenv import load_dotenv

# Add project root to path so we can import src as a package
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.insert(0, project_root)

# Import existing functionality from the codebase
from src import AgentState, SubAgent, create_deep_agent  # noqa: E402
from src.agent import Agent  # noqa: E402
from src.tool_registry import tool  # noqa: E402

# Import existing research tools
from src.tools.internet_search import internet_search  # noqa: E402

# Load environment variables
_ = load_dotenv()


# Simple conversation manager for user interface (new functionality only)
class ConversationInterface:
    """Lightweight interface for user interaction - only what's not in existing codebase"""

    async def get_user_input(self, prompt: str = "") -> str:
        """Get input from user with optional prompt"""
        if prompt:
            print(f"\n🤖 {prompt}")
        print("👤 You: ", end="", flush=True)

        loop = asyncio.get_event_loop()
        user_input = await loop.run_in_executor(None, input)
        return user_input.strip()

    def display_agent_message(self, message: str, message_type: str = "info"):
        """Display agent message to user"""
        icon = (
            "🤖"
            if message_type == "info"
            else "🔍"
            if message_type == "research"
            else "📊"
        )
        print(f"\n{icon} {message}")


# Global interface instance
conversation_interface = ConversationInterface()


@tool(description="Invoke a specialized subagent to handle specific tasks")
async def invoke_subagent(subagent_type: str, task_description: str) -> dict[str, str]:
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
    )
    return await agent.invoke(AgentState())


# NEW FUNCTIONALITY: Conversational tool for user interaction
@tool(
    description="Communicate with the user - ask questions, provide updates, or share findings"
)
def communicate_with_user(
    message: str,
    message_type: Literal["question", "update", "finding", "info"] = "info",
    wait_for_response: bool = True,
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
    conversation_interface.display_agent_message(message, message_type)

    if wait_for_response:
        print("👤 You: ", end="", flush=True)
        user_response = input().strip()
        return {"user_response": user_response}
    else:
        return {"status": "message_sent"}


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
    tools=["communicate_with_user", "internet_search"],
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
        "write_file",
        "communicate_with_user",
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

You must invoke sub-agents to complete the research process."""


class ConversationalResearchAgent:
    """Main class for managing the conversational research experience"""

    def __init__(self):
        from src.agent import Agent  # noqa: E402

        self.agent: Optional[Agent] = None
        self.state: AgentState = AgentState()
        self.interface: ConversationInterface = ConversationInterface()

    async def initialize(self):
        """Initialize the research agent"""
        # Check for API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ Please set ANTHROPIC_API_KEY in your .env file")
            return False

        # Create the main coordinator agent using existing tools + new conversational functionality
        self.agent = create_deep_agent(
            tools=[
                # NEW: Conversational functionality
                communicate_with_user,
                # EXISTING: Research tools
                internet_search,
                invoke_subagent,
                # NOTE: create_deep_agent automatically includes built-in tools:
                # write_todos, invoke_subagent, ls, read_file, write_file
                # (write_file provides filesystem writing functionality)
            ],
            instructions=research_coordinator_instructions,
            subagents=[conversational_researcher, report_writer],
            name="ResearchCoordinator",
            verbose=True,
        )

        return True

    async def start_conversation(self):
        """Start the main conversation loop"""
        print("🚀 Welcome to Conversational Research Assistant!")
        print("=" * 60)
        print(
            "I'm here to help you research any topic through an interactive conversation."
        )
        print(
            "You can ask questions, request clarifications, and guide the research direction."
        )
        print("Type 'quit', 'exit', or 'bye' to end our conversation.\n")

        # Get initial user query
        initial_query = await self.interface.get_user_input(
            "What would you like me to research today?"
        )

        if initial_query.lower() in ["quit", "exit", "bye"]:
            print("👋 Goodbye! Feel free to come back anytime for more research!")
            return

        # Start the conversation with the agent
        self.state.add_message("user", initial_query)

        try:
            # Run the agent with the initial query
            if self.agent is None:
                print("❌ Agent not initialized properly")
                return
            result = await self.agent.invoke(self.state)

            print("\n" + "=" * 60)
            print("🎯 Research Session Complete!")

            # Show final summary
            if result.files:
                print(f"📁 Files created: {list(result.files.keys())}")

                # Save any files to disk
                for filename, content in result.files.items():
                    try:
                        with open(filename, "w", encoding="utf-8") as f:
                            _ = f.write(content)
                        print(f"💾 Saved {filename} to disk")
                    except Exception as e:
                        print(f"❌ Failed to save {filename}: {e}")

            print(f"💬 Total conversation turns: {len(result.messages)}")
            print("\n👋 Thank you for using the Conversational Research Assistant!")

        except KeyboardInterrupt:
            print("\n\n👋 Research session interrupted. Goodbye!")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or contact support if the issue persists.")


async def main():
    """Main function to run the conversational research agent"""
    research_agent = ConversationalResearchAgent()

    # Initialize the agent
    if await research_agent.initialize():
        # Start the conversation loop
        await research_agent.start_conversation()
    else:
        print("❌ Failed to initialize the research agent")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
