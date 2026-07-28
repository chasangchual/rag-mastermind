from __future__ import annotations

from collections import deque

import lmstudio as lms

from app.model.lms import lms_default_client
from app.service.chat.base_chat import ChatProvider

SYSTEM_PROMPT = "You are a helpful and funny assistant."
MAX_HISTORY_TURNS = 10  # ponytail: fixed-size trim, move to summarization if that's not enough context


class LMStudioChatProvider(ChatProvider):
    def __init__(self, max_history_turns: int = MAX_HISTORY_TURNS) -> None:
        self._model = lms_default_client.llm.model()
        self._history: deque[tuple[str, str]] = deque(maxlen=max_history_turns)

    def ask(self, question: str) -> str:
        chat = lms.Chat(SYSTEM_PROMPT)
        for user_message, assistant_message in self._history:
            chat.add_user_message(user_message)
            chat.add_assistant_response(assistant_message)
        chat.add_user_message(question)

        answer = self._model.respond(chat).content
        self._history.append((question, answer))
        return answer

    def reset(self) -> None:
        self._history.clear()


lmstudio_chat_provider = LMStudioChatProvider()
