from __future__ import annotations

from collections import deque

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.service.chat.base_chat import ChatProvider
from app.config.app_config import get_config

SYSTEM_PROMPT = "You are a helpful and funny assistant."
MAX_HISTORY_TURNS = 10  # ponytail: fixed-size trim, move to summarization if that's not enough context
GEMINI_CHAT_MODEL = "gemini-3.6-flash"


class GeminiChatProvider(ChatProvider):
    def __init__(self, max_history_turns: int = MAX_HISTORY_TURNS) -> None:
        config = get_config()
        self._model = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL, api_key=config.gemini_api_key, temperature=0.0)
        self._history: deque[tuple[str, str]] = deque(maxlen=max_history_turns)

    def ask(self, question: str) -> str:
        messages = [SystemMessage(SYSTEM_PROMPT)]
        for user_message, assistant_message in self._history:
            messages.append(HumanMessage(user_message))
            messages.append(AIMessage(assistant_message))
            messages.append(HumanMessage(question))

        answer = self._model.invoke(messages).text
        self._history.append((question, answer))
        return answer

    def reset(self) -> None:
        self._history.clear()
