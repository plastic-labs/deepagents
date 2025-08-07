from typing import List, Dict, Any, Optional, Callable
import json
from .state import AgentState
from .tools import registry
from .llm import LLMClient


class SubAgent:
    def __init__(
        self, name: str, description: str, prompt: str, tools: List[str] = None
    ):
        self.name = name
        self.description = description
        self.prompt = prompt
        self.tools = tools or []


class ConversationManager:
    def __init__(self, model: str = "claude-3-5-haiku-20241022"):
        self.llm = LLMClient(model)
        self.max_iterations = 50

    async def invoke(
        self, state: AgentState, tool_names: List[str], system_prompt: str
    ) -> AgentState:
        messages = state.get_messages()

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
            response = await self.llm.invoke(messages, tool_schemas, system_prompt)

            if response.get("content"):
                content = response["content"]
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "text":
                            state.add_message("assistant", item["text"])
                        elif item.get("type") == "tool_use":
                            tool_name = item["name"]
                            tool_args = item["input"]
                            
                            try:
                                result = registry.execute(tool_name, tool_args, state)
                                messages.append(
                                    {
                                        "role": "user",
                                        "content": f"Tool {tool_name} returned: {json.dumps(result, indent=2)}",
                                    }
                                )
                            except Exception as e:
                                messages.append(
                                    {
                                        "role": "user",
                                        "content": f"Error executing {tool_name}: {str(e)}",
                                    }
                                )
                else:
                    state.add_message("assistant", str(content))
                    break

            if not response.get("content") or not any(
                item.get("type") == "tool_use" for item in response.get("content", [])
            ):
                break

        return state


class Agent:
    def __init__(
        self,
        tools: List[Any],
        instructions: str,
        model: str = "claude-3-5-haiku-20241022",
    ):
        self.tools = tools
        self.instructions = instructions
        self.conversation = ConversationManager(model)
    
    async def invoke(self, state: AgentState) -> AgentState:
        # Register tools with registry
        for tool_func in self.tools:
            if callable(tool_func):
                registry.tools[tool_func.__name__] = tool_func
            else:
                # Handle string names
                registry.tools[str(tool_func)] = str(tool_func)
        
        tool_names = [tool.__name__ if callable(tool) else str(tool) for tool in self.tools]
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