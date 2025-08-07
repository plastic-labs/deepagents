from dataclasses import dataclass
from enum import Enum
from typing import Optional

from honcho import Honcho


class TodoStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Todo:
    content: str
    status: TodoStatus = TodoStatus.PENDING


class AgentState:
    """
    Manages agent state using Honcho's Python SDK for conversation memory,
    peer representations, and session management.
    """

    def __init__(self, session_id: str, workspace_id: str = "deepagents"):
        """
        Initialize AgentState with Honcho integration.

        Args:
            workspace_id: The Honcho workspace identifier
            session_id: The session identifier for this conversation
        """
        self.honcho = Honcho(environment="production", workspace_id=workspace_id)
        self.session_id = session_id

        # Create peers for agent and user
        self.agent_peer = self.honcho.peer("agent", config={"observe_me": False})
        self.user_peer = self.honcho.peer("user")

        # Get or create session
        self.session = self.honcho.session(session_id)

        # Add peers to session
        self.session.add_peers([self.agent_peer, self.user_peer])

        # Local state for todos (not managed by Honcho)
        self.todos: list[Todo] = []

    def add_message(
        self, role: str, content: str, metadata: Optional[dict] = None
    ) -> None:
        """
        Add a message to the conversation session.

        Args:
            role: The role of the message sender ("user" or "agent")
            content: The message content
            metadata: Optional metadata for the message
        """
        if role == "user":
            message = self.user_peer.message(content, metadata=metadata or {})
        else:
            message = self.agent_peer.message(content, metadata=metadata or {})

        self.session.add_messages([message])

    def get_messages(self) -> list[dict[str, str]]:
        """
        Get all messages from the current session.

        Returns:
            List of message dictionaries with role and content
        """
        messages = self.session.get_context(summary=False).to_anthropic(
            assistant=self.agent_peer
        )
        return messages

    def query_agent_knowledge(
        self, query: str, target_peer: Optional[str] = None
    ) -> str:
        """
        Query the agent's knowledge representation.

        Args:
            query: The natural language query
            target_peer: Optional target peer to query about

        Returns:
            Response from the agent's knowledge
        """
        if target_peer:
            return self.agent_peer.chat(query, target=target_peer)
        return self.agent_peer.chat(query)

    def query_user_knowledge(
        self, query: str, target_peer: Optional[str] = None
    ) -> str:
        """
        Query the user's knowledge representation.

        Args:
            query: The natural language query
            target_peer: Optional target peer to query about

        Returns:
            Response from the user's knowledge
        """
        if target_peer:
            return self.user_peer.chat(query, target=target_peer)
        return self.user_peer.chat(query)

    def search_conversation(self, query: str) -> list:
        """
        Search through conversation content.

        Args:
            query: Search query

        Returns:
            List of search results
        """
        return self.session.search(query)

    def add_todo(self, content: str) -> None:
        """
        Add a todo item to local state.

        Args:
            content: The todo content
        """
        self.todos.append(Todo(content=content))

    def update_todo_status(self, content: str, status: TodoStatus) -> None:
        """
        Update the status of a todo item.

        Args:
            content: The todo content to match
            status: The new status
        """
        for todo in self.todos:
            if todo.content == content:
                todo.status = status
                break

    def get_todos(self) -> list[Todo]:
        """
        Get all todo items.

        Returns:
            List of Todo objects
        """
        return self.todos

    def set_session_metadata(self, metadata: dict) -> None:
        """
        Set metadata for the current session.

        Args:
            metadata: Dictionary of metadata
        """
        self.session.set_metadata(metadata)

    def get_session_metadata(self) -> dict:
        """
        Get metadata for the current session.

        Returns:
            Session metadata dictionary
        """
        return self.session.get_metadata()

    def create_new_session(self, session_id: str) -> None:
        """
        Create and switch to a new session.

        Args:
            session_id: The new session identifier
        """
        self.session_id = session_id
        self.session = self.honcho.session(session_id)
        self.session.add_peers([self.agent_peer, self.user_peer])
