"""
Conversational memory service.

Maintains a sliding window of recent interactions per session
so that the LLM can produce contextually-aware follow-up answers.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Interaction:
    """A single user ↔ assistant exchange."""
    question: str
    answer: str


class MemoryService:
    """
    In-memory conversational history with configurable window size.

    Each *session_id* gets its own independent history buffer.
    When the buffer exceeds ``max_window`` interactions, the oldest
    entries are evicted automatically.

    Attributes:
        max_window: Maximum number of interactions to retain per session.
    """

    def __init__(self, max_window: int = 5) -> None:
        """
        Initialise the memory service.

        Args:
            max_window: Number of recent interactions to keep.
        """
        self.max_window: int = max_window
        self._store: Dict[str, List[Interaction]] = defaultdict(list)
        logger.info("MemoryService initialised (window=%d).", max_window)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, session_id: str, question: str, answer: str) -> None:
        """
        Record a new interaction for *session_id*.

        If the window limit is exceeded the oldest interaction is removed.

        Args:
            session_id: Unique identifier for the conversation session.
            question: The user's question.
            answer: The assistant's answer.
        """
        history = self._store[session_id]
        history.append(Interaction(question=question, answer=answer))

        # Evict oldest if over limit
        if len(history) > self.max_window:
            history.pop(0)

        logger.debug(
            "Session %s: stored interaction (%d/%d).",
            session_id,
            len(history),
            self.max_window,
        )

    def get_history(self, session_id: str) -> List[Tuple[str, str]]:
        """
        Return the conversation history for *session_id*.

        Args:
            session_id: Unique identifier for the conversation session.

        Returns:
            A list of ``(question, answer)`` tuples, oldest first.
        """
        return [
            (interaction.question, interaction.answer)
            for interaction in self._store.get(session_id, [])
        ]

    def get_formatted_history(self, session_id: str) -> str:
        """
        Return a human-readable conversation transcript for prompt injection.

        Args:
            session_id: Unique identifier for the conversation session.

        Returns:
            A formatted string of the conversation history.
        """
        history = self.get_history(session_id)
        if not history:
            return "No previous conversation."

        lines: list[str] = []
        for q, a in history:
            lines.append(f"User: {q}")
            lines.append(f"Assistant: {a}")
        return "\n".join(lines)

    def clear(self, session_id: str) -> None:
        """
        Clear all stored interactions for *session_id*.

        Args:
            session_id: Unique identifier for the conversation session.
        """
        self._store.pop(session_id, None)
        logger.info("Cleared memory for session %s.", session_id)

    def clear_all(self) -> None:
        """Clear all session histories."""
        self._store.clear()
        logger.info("Cleared all conversation memory.")

    @property
    def active_sessions(self) -> int:
        """Return the number of sessions with stored history."""
        return len(self._store)
