from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque

MAX_HISTORY_TURNS = 10  # ponytail: fixed-size trim, move to summarization if that's not enough context

class ChatProvider(ABC):
    def __init__(self, max_history_turns: int = MAX_HISTORY_TURNS) -> None:
        self._history: deque[tuple[str, str]] = deque(maxlen=max_history_turns)

    @abstractmethod
    def ask(self, question: str) -> str:
        raise NotImplementedError

    def reset(self) -> None:
        self._history.clear()
