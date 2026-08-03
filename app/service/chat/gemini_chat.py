from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.service.chat.base_chat import ChatProvider, MAX_HISTORY_TURNS
from app.config.app_config import get_config

SYSTEM_PROMPT = "You are a helpful and funny assistant."
GEMINI_CHAT_MODEL = "gemini-3.6-flash"

logger = logging.getLogger(__name__)

class GeminiChatProvider(ChatProvider):
    def __init__(self, max_history_turns: int = MAX_HISTORY_TURNS) -> None:
        super().__init__(max_history_turns)
        
        config = get_config()
        self._model = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL, api_key=config.gemini_api_key, temperature=0.0)

    def ask(self, question: str) -> str:
        messages = [SystemMessage(SYSTEM_PROMPT)]

        for user_message, assistant_message in self._history:
            messages.append(HumanMessage(user_message))
            messages.append(AIMessage(assistant_message))

        messages.append(HumanMessage(question))

        try:
            answer = self._model.invoke(messages).text
        except Exception as e:
            logger.error("Error occurred while invoking GEMINI model: %s", e)
            raise
        self._history.append((question, answer))
        return answer