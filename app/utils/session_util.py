import asyncio
import secrets
from typing import Optional
import uuid
from fastapi import Response, WebSocket

SESSION_ID_NAME = "mastermind_session_id"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days
SESSION_ID_LENGTH = 64

def get_session_id(raw_session_id) -> str:
    if isinstance(raw_session_id, str) and raw_session_id.strip():
        return SessionUtils.get_or_create_session_id(raw_session_id.strip())
    return SessionUtils.get_or_create_session_id(None)

class SessionUtils:
    @staticmethod
    def get_or_create_session_id(existing_id: Optional[str]) -> str:
        if existing_id and len(existing_id) == SESSION_ID_LENGTH:
            return existing_id
        return secrets.token_hex(SESSION_ID_LENGTH // 2)

    @staticmethod
    def set_session_cookie(response: Response, session_id: str):
        response.set_cookie(
            key=SESSION_ID_NAME,
            value=session_id,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
