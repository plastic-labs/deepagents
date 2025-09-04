import json
import uuid
from typing import Any, Callable, cast

from .agent_state import AgentState
from .llm import LLMClient
from .tool_registry import registry
from .tools import complete_task, invoke_subagent


class SubAgent:
    def __init__(
        self,
        name: str,
        description: str,
        tools: list[Callable],
        instructions: str,
        model: str = "claude-4-sonnet-20250514",
        verbose: bool = True,
        max_iterations: int = 50,
    ):
        self.name: str = name
        self.description: str = description
        self.tools: list[Callable] = tools
        self.instructions: str = instructions
        self.model = model
        self.verbose = verbose
        self.max_iterations = max_iterations


class Agent:
    def __init__(
        self,
        name: str,
        tools: list[Callable],
        instructions: str,
        session_id: str = str(uuid.uuid4()),
        model: str = "claude-4-sonnet-20250514",
        verbose: bool = True,
        subagents: list[SubAgent] = None,
        max_iterations: int = 50,
        is_subagent: bool = False,
    ):
        self.name: str = name

        extra_tools = []

        if subagents:
            extra_tools.append(invoke_subagent)

        if not is_subagent:
            extra_tools.append(complete_task)

        self.tools: list[Callable] = tools + extra_tools
        self.instructions: str = instructions
        if is_subagent:
            self.instructions += "\n\nIMPORTANT: You are a subagent. When you have completed your task, provide your final result in your last message. Do not use complete_task as that tool is not available to you."

        self.subagents: dict[str, SubAgent] = {s.name: s for s in subagents or []}
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.is_subagent = is_subagent
        self.state = AgentState(peer_id=self.name, session_id=session_id)
        self.llm = LLMClient(model=model)

    def _log(self, message: str, level: str = "INFO"):
        """Log agent dialogue with formatting"""
        if self.verbose:
            print(
                f"💬 [{self.name}]: {message}"
                if level == "INFO"
                else f"🔧 [{self.name}] {message}"
            )

    def invoke(
        self, first_message: str = "Hello", *, parent_agent: str | None = None
    ) -> str:
        tool_names = [tool.__name__ for tool in self.tools]

        system_prompt = self.instructions

        if self.tools:
            system_prompt += """

You have access to the following tools to complete the task:
""" + "\n".join([f"- {name}: {registry.get_description(name)}" for name in tool_names])

        if self.subagents:
            system_prompt += (
                """

You have access to the following subagents to complete the task:
"""
                + "\n".join(
                    [
                        f"- {subagent.name}: {subagent.description}"
                        for subagent in self.subagents.values()
                    ]
                )
                + """

Use subagents by calling the `invoke_subagent` tool. If subagents are provided, you should make use of them to complete the task if at all possible.
"""
            )

        if not self.is_subagent:
            system_prompt += """

When you are done, you should call the `complete_task` tool to tell the user the result. The user will **only** see the text given to this tool. The user will now send a message describing the task.
"""
        else:
            system_prompt += """
            
You are a subagent. When you have completed your task, provide your final result in a comprehensive response. Do NOT continue making additional tool calls after you have sufficient information to answer the question. Stop as soon as you have a complete answer.
"""

        self._log(f"Starting task with {len(tool_names)} available tools", "DEBUG")
        if tool_names:
            self._log(f"Tools: {', '.join(tool_names)}", "DEBUG")

        tool_schemas: list[dict[str, Any]] = [
            registry.get_schema(tool_name) for tool_name in tool_names
        ]

        # Add the first message to kick off this task
        self.state.add_message(parent_agent or "User", first_message)

        last_text_response = ""

        for iteration in range(self.max_iterations):
            messages = self.state.get_messages()

            self._log(
                f"Iteration {iteration + 1}/{self.max_iterations} - Thinking...",
                "DEBUG",
            )
            response = self.llm.invoke(messages, tool_schemas, system_prompt)

            if response.get("content"):
                content: list[dict[str, Any]] | dict[str, Any] = response["content"]
                has_tool_calls = False

                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "text":
                            last_text_response = item["text"]
                        if item.get("type") == "tool_use":
                            has_tool_calls = True
                        result = self._handle_content_item(item)
                        if result:
                            return result
                else:
                    if content.get("type") == "text":
                        last_text_response = content["text"]
                    if content.get("type") == "tool_use":
                        has_tool_calls = True
                    result = self._handle_content_item(content)
                    if result:
                        return result

                # if we got a text response but no tool calls, and we have some content, stop here
                if not has_tool_calls and last_text_response.strip():
                    return last_text_response

            else:
                self._log("No response from LLM", "DEBUG")
                break

        # For subagents, return the last text response instead of failing
        if self.is_subagent:
            return last_text_response

        self._log(f"Task failed after {iteration + 1} iterations", "DEBUG")

    def _handle_content_item(self, item: dict[str, Any]) -> str | None:
        if item.get("type") == "text":
            response_text = item["text"]
            self._log(f"{response_text}")
            self.state.add_message(self.name, response_text)
            return None
        elif item.get("type") == "tool_use":
            tool_name = item["name"]
            tool_args = item["input"]
            return self._execute_tool_call(tool_name, tool_args)

    def _execute_tool_call(
        self, tool_name: str, tool_args: dict[str, Any]
    ) -> str | None:
        if tool_name == "complete_task":
            self.state.add_message(self.name, tool_args["result"])
            return cast(str, tool_args["result"])

        self._log(f"Using tool: {tool_name} with args: {tool_args}", "TOOL")

        if tool_name == "invoke_subagent":
            subagent_name = tool_args["subagent_name"]
            subagent_prompt = tool_args["prompt"]
            subagent = self.subagents.get(subagent_name)
            if not subagent:
                self._log(f"Subagent {subagent_name} not found", "TOOL")
                return None
            # the result will be added to message history by the subagent
            run_subagent(subagent, self.name, self.state.session_id, subagent_prompt)
            return None

        try:
            result = registry.execute(name=tool_name, arguments=tool_args)
            result_preview = (
                str(result)[:150] + "..." if len(str(result)) > 150 else str(result)
            )
            self._log(f"Tool {tool_name} result: {result_preview}", "TOOL")

            if tool_name == "communicate_with_user":
                self.state.add_message(
                    self.name,
                    tool_args["message"],
                )
                self.state.add_message(
                    "User",
                    result["user_response"],
                )
            else:
                self.state.add_message(
                    "tool-caller",
                    f"Tool {tool_name} returned: {json.dumps(result, indent=2)}",
                )

        except Exception as e:
            self._log(f"Tool {tool_name} failed: {str(e)}", "TOOL")
            self.state.add_message(
                "tool-caller", f"Error executing {tool_name}: {str(e)}"
            )

        return None


def run_subagent(
    subagent: SubAgent, parent_agent_name: str, session_id: str, prompt: str
) -> str:
    # Create an agent in subagent mode (excludes complete_task tool)
    subagent_runner = Agent(
        name=subagent.name,
        tools=subagent.tools,
        instructions=subagent.instructions,
        session_id=session_id,
        model=subagent.model,
        verbose=subagent.verbose,
        max_iterations=subagent.max_iterations,
        is_subagent=True,
    )
    return subagent_runner.invoke(prompt, parent_agent=parent_agent_name)


def create_deep_agent(
    name: str,
    tools: list[Callable],
    instructions: str,
    session_id: str = str(uuid.uuid4()),
    model: str = "claude-4-sonnet-20250514",
    subagents: list[SubAgent] = None,
    verbose: bool = True,
) -> Agent:
    """Create a deep agent with built-in tools and optional subagents."""

    return Agent(
        name,
        tools,
        instructions,
        session_id=session_id,
        model=model,
        verbose=verbose,
        subagents=subagents,
    )
