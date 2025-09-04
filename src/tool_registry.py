import inspect
from functools import wraps
from typing import Any, Callable, get_type_hints


class ToolRegistry:
    """
    ToolRegistry: a set of tools and their schemas that are available to the agent.
    """

    def __init__(self):
        self.tools: dict[str, Callable] = {}
        self.schemas: dict[str, dict[str, Any]] = {}

    def tool(self, description: str = ""):
        def decorator(func: Callable) -> Callable:
            name = func.__name__
            self.tools[name] = func
            self.schemas[name] = self._generate_schema(func, description)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def _generate_schema(self, func: Callable, description: str) -> dict[str, Any]:
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        schema = {
            "name": func.__name__,
            "description": description or func.__doc__ or "",
            "input_schema": {"type": "object", "properties": {}, "required": []},
        }

        for param_name, param in sig.parameters.items():
            if param_name in ["state", "tool_call_id"]:
                continue

            param_schema = {
                "type": self._python_type_to_json_type(type_hints.get(param_name, str))
            }
            schema["input_schema"]["properties"][param_name] = param_schema

            if param.default == inspect.Parameter.empty:
                schema["input_schema"]["required"].append(param_name)

        return schema

    def _python_type_to_json_type(self, py_type: type) -> str:
        if py_type is str:
            return "string"
        elif py_type is int:
            return "integer"
        elif py_type is float:
            return "number"
        elif py_type is bool:
            return "boolean"
        elif hasattr(py_type, "__origin__") and py_type.__origin__ is list:
            return "array"
        elif hasattr(py_type, "__origin__") and py_type.__origin__ is dict:
            return "object"
        else:
            return "string"

    def get_tools(self) -> list[str]:
        return list(self.tools.keys())

    def get_schema(self, name: str) -> dict[str, Any]:
        return self.schemas.get(name, {})

    def get_description(self, name: str) -> str:
        return self.schemas.get(name, {}).get("description", "")

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")

        func = self.tools[name]
        return func(**arguments)


registry = ToolRegistry()
tool = registry.tool
