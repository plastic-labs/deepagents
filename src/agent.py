import json
from typing import Any, Optional, Callable

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
        self.tools: list[Callable] = tools or []


class Agent:
    def __init__(
        self,
        tools: list[Any],
        instructions: str,
        model: str = "claude-4-sonnet-20250514",
        name: str = "Agent",
        verbose: bool = True,
        subagents: list[SubAgent] = None,
        max_iterations: int = 50,
        session_id: str = str(uuid.uuid4()),
    ):
        self.tools: list[Any] = tools
        self.instructions: str = instructions
        self.name: str = name
        self.subagents: list[SubAgent] = subagents or []
        self.verbose = True
        self.max_iterations = max_iterations
        self.state = AgentState(peer_id=self.name, session_id=session_id)
        self.llm = LLMClient(model=model)

    def _log(self, message: str, level: str = "INFO"):
        """Log agent dialogue with formatting"""
        if self.verbose:
            prefix = f"🤖 [{self.name}]" if level == "INFO" else f"🔧 [{self.name}]"
            print(f"{prefix} {message}")

    def invoke(self):
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
            messages = self.state.get_messages()
            if len(messages) == 0:
                messages = [{"role": "user", "content": "Hello"}]

            self._log(f"Iteration {iteration + 1}/{self.max_iterations} - Thinking...")
            response = self.llm.invoke(messages, tool_schemas, system_prompt)

            if response.get("content"):
                content = response["content"]
                if isinstance(content, list):
                    text_responses = []
                    tool_calls = []

                    for item in content:
                        if item.get("type") == "text":
                            text_responses.append(item["text"])
                            print("==================")
                            print(content)
                            print("==================")
                            self.state.add_message("tool-caller", item["text"])
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
                        self.state.add_message(self.name, response_preview)

                    # Log and execute tool calls
                    for tool_name, tool_args in tool_calls:
                        self._log(
                            f"Using tool: {tool_name} with args: {tool_args}", "TOOL"
                        )

                        try:
                            result = registry.execute(
                                name=tool_name, arguments=tool_args
                            )
                            result_preview = (
                                str(result)[:150] + "..."
                                if len(str(result)) > 150
                                else str(result)
                            )
                            self._log(
                                f"Tool {tool_name} result: {result_preview}", "TOOL"
                            )

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
                else:
                    response_text = str(content)
                    response_preview = (
                        response_text[:100] + "..."
                        if len(response_text) > 100
                        else response_text
                    )
                    self._log(f"Final response: {response_preview}")
                    self.state.add_message(self.name, response_text)
                    break

            if not response.get("content") or not any(
                item.get("type") == "tool_use" for item in response.get("content", [])
            ):
                break

        self._log(f"Conversation completed after {iteration + 1} iterations")
