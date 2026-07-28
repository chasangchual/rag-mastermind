from __future__ import annotations

from abc import ABC, abstractmethod


class ChatProvider(ABC):
    @abstractmethod
    def ask(self, question: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
