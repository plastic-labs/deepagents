import inspect
from functools import wraps
from typing import Dict, List, Any, Callable, get_type_hints
import json


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}
    
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
    
    def _generate_schema(self, func: Callable, description: str) -> Dict[str, Any]:
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        schema = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description or func.__doc__ or "",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        for param_name, param in sig.parameters.items():
            if param_name in ["state", "tool_call_id"]:
                continue
                
            param_schema = {"type": self._python_type_to_json_type(type_hints.get(param_name, str))}
            schema["function"]["parameters"]["properties"][param_name] = param_schema
            
            if param.default == inspect.Parameter.empty:
                schema["function"]["parameters"]["required"].append(param_name)
        
        return schema
    
    def _python_type_to_json_type(self, py_type: type) -> str:
        if py_type == str:
            return "string"
        elif py_type == int:
            return "integer"
        elif py_type == float:
            return "number"
        elif py_type == bool:
            return "boolean"
        elif hasattr(py_type, '__origin__') and py_type.__origin__ == list:
            return "array"
        elif hasattr(py_type, '__origin__') and py_type.__origin__ == dict:
            return "object"
        else:
            return "string"
    
    def get_tools(self) -> List[str]:
        return list(self.tools.keys())
    
    def get_schema(self, name: str) -> Dict[str, Any]:
        return self.schemas.get(name, {})
    
    def execute(self, name: str, arguments: Dict[str, Any], state=None) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        
        func = self.tools[name]
        sig = inspect.signature(func)
        
        kwargs = arguments.copy()
        if "state" in sig.parameters:
            kwargs["state"] = state
        
        return func(**kwargs)


registry = ToolRegistry()
tool = registry.tool