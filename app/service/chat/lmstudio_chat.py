from __future__ import annotations

import lmstudio as lms

from app.model.lms import call_with_reconnect
from app.service.chat.base_chat import ChatProvider, MAX_HISTORY_TURNS

SYSTEM_PROMPT = "You are a helpful and funny assistant."


class LMStudioChatProvider(ChatProvider):
    def ask(self, question: str) -> str:
        chat = lms.Chat(SYSTEM_PROMPT)
        for user_message, assistant_message in self._history:
            chat.add_user_message(user_message)
            chat.add_assistant_response(assistant_message)
        chat.add_user_message(question)

        answer = call_with_reconnect(lambda client: client.llm.model().respond(chat).content)
        self._history.append((question, answer))
        return answer

    def reset(self) -> None:
        self._history.clear()


# lmstudio_chat_provider = LMStudioChatProvider()
