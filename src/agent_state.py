from typing import Optional

from honcho import Honcho
from honcho.session import MessageCreateParam


class AgentState:
    """
    Manages agent state using Honcho's Python SDK for conversation memory,
    peer representations, and session management.
    """

    def __init__(
        self,
        peer_id: str,
        session_id: str,
        workspace_id: str = "deepagents",
    ):
        """
        Initialize AgentState with Honcho integration.

        Args:
            workspace_id: The Honcho workspace identifier
            session_id: The session identifier for this conversation
        """
        self.honcho = Honcho(environment="production", workspace_id=workspace_id)
        self.session_id = session_id

        self.peer_id = peer_id

        # Get or create peer
        self.peer = self.honcho.peer(peer_id, config={"observe_me": False})

        # Get or create session
        self.session = self.honcho.session(
            session_id, config={"deriver_disabled": True}
        )

    def add_message(self, peer_name: str, content: str, metadata: dict = {}) -> None:
        """
        Add a message to the conversation session.

        Args:
            role: The role of the message sender ("user" or "agent")
            content: The message content
            metadata: Optional metadata for the message
        """
        self.session.add_messages(
            [MessageCreateParam(content=content, peer_id=peer_name, metadata=metadata)]
        )

    def get_messages(self) -> list[dict[str, str]]:
        """
        Get all messages from the current session.

        Returns:
            List of message dictionaries with role and content
        """

        messages = self.session.get_context(summary=False).to_anthropic(
            assistant=self.peer_id
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
            return self.honcho.peer(self.peer_id).chat(query, target=target_peer)
        return self.honcho.peer(self.peer_id).chat(query)

    def search_conversation(self, query: str) -> list:
        """
        Search through conversation content.

        Args:
            query: Search query

        Returns:
            List of search results
        """
        return self.session.search(query)

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
