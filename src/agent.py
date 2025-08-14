import json
from typing import Any, Optional

from .llm import LLMClient
from .state import AgentState
from .tool_registry import registry
import uuid


class SubAgent:
    def __init__(
        self,
        name: str,
        description: str,
        prompt: str,
        tools: Optional[list[str]] = None,
    ):
        self.name: str = name
        self.description: str = description
        self.prompt: str = prompt
        self.tools: list[str] = tools or []


class ConversationManager:
    def __init__(
        self,
        model: str = "claude-4-sonnet-20250514",
        agent_name: str = "Agent",
        verbose: bool = True,
    ):
        self.llm: LLMClient = LLMClient(model)
        self.max_iterations: int = 50
        self.agent_name: str = agent_name
        self.verbose: bool = verbose

    def _log(self, message: str, level: str = "INFO"):
        """Log agent dialogue with formatting"""
        if self.verbose:
            prefix = (
                f"🤖 [{self.agent_name}]"
                if level == "INFO"
                else f"🔧 [{self.agent_name}]"
            )
            print(f"{prefix} {message}")

    async def invoke(
        self, state: AgentState, tool_names: list[str], system_prompt: str
    ) -> AgentState:
        messages = state.get_messages()

        self._log(f"Starting conversation with {len(tool_names)} available tools")
        if tool_names:
            self._log(f"Available tools: {', '.join(tool_names)}")

        tool_schemas = []
        for tool_name in tool_names:
            schema = registry.get_schema(tool_name)
            tool_schemas.append(
                {
                    "name": tool_name,
                    "description": schema.get("function", {}).get("description", ""),
                    "input_schema": schema.get("function", {}).get(
                        "parameters", {"type": "object", "properties": {}}
                    ),
                }
            )

        for iteration in range(self.max_iterations):
            self._log(f"Iteration {iteration + 1}/{self.max_iterations} - Thinking...")
            response = await self.llm.invoke(messages, tool_schemas, system_prompt)

            if response.get("content"):
                content = response["content"]
                if isinstance(content, list):
                    text_responses = []
                    tool_calls = []

                    for item in content:
                        if item.get("type") == "text":
                            text_responses.append(item["text"])
                            state.add_message("assistant", item["text"])
                        elif item.get("type") == "tool_use":
                            tool_name = item["name"]
                            tool_args = item["input"]
                            tool_calls.append((tool_name, tool_args))

                    # Log agent response
                    if text_responses:
                        response_preview = (
                            " ".join(text_responses)[:100] + "..."
                            if len(" ".join(text_responses)) > 100
                            else " ".join(text_responses)
                        )
                        self._log(f"Response: {response_preview}")

                    # Log and execute tool calls
                    for tool_name, tool_args in tool_calls:
                        self._log(
                            f"Using tool: {tool_name} with args: {tool_args}", "TOOL"
                        )

                        try:
                            result = registry.execute(tool_name, tool_args, state)
                            result_preview = (
                                str(result)[:150] + "..."
                                if len(str(result)) > 150
                                else str(result)
                            )
                            self._log(
                                f"Tool {tool_name} result: {result_preview}", "TOOL"
                            )
                            messages.append(
                                {
                                    "role": "user",
                                    "content": f"Tool {tool_name} returned: {json.dumps(result, indent=2)}",
                                }
                            )
                        except Exception as e:
                            self._log(f"Tool {tool_name} failed: {str(e)}", "TOOL")
                            messages.append(
                                {
                                    "role": "user",
                                    "content": f"Error executing {tool_name}: {str(e)}",
                                }
                            )
                else:
                    response_text = str(content)
                    response_preview = (
                        response_text[:100] + "..."
                        if len(response_text) > 100
                        else response_text
                    )
                    self._log(f"Final response: {response_preview}")
                    state.add_message("assistant", response_text)
                    break

            if not response.get("content") or not any(
                item.get("type") == "tool_use" for item in response.get("content", [])
            ):
                break

        self._log(f"Conversation completed after {iteration + 1} iterations")
        return state


class Agent:
    def __init__(
        self,
        tools: list[Any],
        instructions: str,
        model: str = "claude-4-sonnet-20250514",
        name: str = "Agent",
        verbose: bool = True,
        subagents: list[SubAgent] = None,
        state: AgentState = None,
    ):
        self.tools: list[Any] = tools
        self.instructions: str = instructions
        self.name: str = name
        self.conversation: ConversationManager = ConversationManager(
            model, agent_name=name, verbose=verbose
        )
        self.subagents: list[SubAgent] = subagents or []
        if state:
            self.state = state
        else:
            self.conversation.state = AgentState(str(uuid.uuid4()))

    async def invoke(self):
        # Register tools with registry
        for tool_func in self.tools:
            if callable(tool_func):
                registry.tools[tool_func.__name__] = tool_func
            else:
                # Handle string names
                registry.tools[str(tool_func)] = str(tool_func)

        tool_names = [
            tool.__name__ if callable(tool) else str(tool) for tool in self.tools
        ]
        system_prompt = (
            self.instructions
            + """

You have access to the following tools:
"""
            + "\n".join(
                [
                    f"- {name}: {registry.get_schema(name).get('function', {}).get('description', '')}"
                    for name in tool_names
                ]
            )
        )

        return await self.conversation.invoke(state, tool_names, system_prompt)
