from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class TodoStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Todo:
    content: str
    status: TodoStatus = TodoStatus.PENDING


@dataclass
class AgentState:
    messages: List[Dict[str, str]] = field(default_factory=list)
    todos: List[Todo] = field(default_factory=list)
    files: Dict[str, str] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages
    
    def add_todo(self, content: str) -> None:
        self.todos.append(Todo(content=content))
    
    def update_todo_status(self, content: str, status: TodoStatus) -> None:
        for todo in self.todos:
            if todo.content == content:
                todo.status = status
                break
    
    def get_files(self) -> Dict[str, str]:
        return self.files
    
    def update_file(self, path: str, content: str) -> None:
        self.files[path] = content
    
    def get_file(self, path: str) -> Optional[str]:
        return self.files.get(path)