from shutil import unregister_archive_format

from fastapi import APIRouter, Request, Cookie, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from typing import Any, Optional
import secrets
from enum import Enum
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, timezone
from app.utils.session_util import SESSION_ID_NAME, SessionUtils, get_session_id
from app.utils.date_util import now_utc_iso

from app.utils.session_util import SESSION_ID_NAME, SessionUtils

class CHAT_MESSAGE_TYPE(Enum):
    UNKNOWN = "unknown"
    HELLO = "mastermind_rag_chat_hello"
    READY = "connection_ready"
    USER_MESSAGE = "user_message"
    SYSTEM_MESSAGE = "system_message"
    PING = "ping"
    
def get_message_type(type:str) -> CHAT_MESSAGE_TYPE:
    try:
        return CHAT_MESSAGE_TYPE(type)
    except ValueError:
        return CHAT_MESSAGE_TYPE.UNKNOWN
     
class CHAT_ERROR_TYPE(Enum):
    INVALID_HELLO = "invalid greeting message"
    INVALID_TYPE= "invalid message type"

DEFAULT_ASSISTANT_MESSAGE = (
    "This is a placeholder WebSocket response from FastAPI. "
    "The RAG pipeline is not connected yet. Later, this handler can call your "
    "retriever, embedding/vector store, reranker, and LLM service."
)
CHAT_MEMORY: dict[str, list[dict[str, Any]]] = {}

chat_router = APIRouter(
    prefix="/app/chat"
)

async def push_error_message(websocket: WebSocket, type: CHAT_ERROR_TYPE, close_after: bool = False):
    await websocket.send_json({
        "type": "error",
        "error": type.value,
         "created_at": now_utc_iso(),
    })
    
    if(close_after):
        await websocket.close(code=1002)

async def push_system_message(websocket: WebSocket, type: CHAT_MESSAGE_TYPE, session_id: str, text: str):
    await websocket.send_json({
        "type": type.value,
        "session_id": session_id,
        "text": text,
        "created_at": now_utc_iso(),
    })

async def build_response(user_text: str, session_id: str) -> dict[str, Any]:
    """Temporary backend placeholder for the future RAG implementation."""
    return {
        "role": "assistant",
        "content": DEFAULT_ASSISTANT_MESSAGE,
        "created_at": now_utc_iso(),
        "meta": {
            "session_id": session_id,
            "placeholder": True,
            "received_text_length": len(user_text),
            "retrieval": {
                "mode": "traditional_rag_placeholder",
                "top_k": 8,
                "threshold": 0.72,
                "chunks": [
                    {
                        "id": "placeholder-chunk-001",
                        "source": "document_library_placeholder",
                        "score": 0.88,
                        "preview": "Retrieved chunk preview will appear here after RAG is implemented.",
                    }
                ],
            },
        },
    }
        
@chat_router.websocket("/ws")
async def ws_chat(websocket: WebSocket):
    """Chat WebSocket endpoint.
    Protocol:
    1. Client connects to /app/chat/ws.
    2. Client sends: {"type": "mastermind_rag_chat_hello", "session_id": "..."}
    3. Client sends: {"type": "user_message", "text": "..."}
    4. Server returns ack/typing/assistant_message events.
    """
    await websocket.accept()

    try:
        greeting = await websocket.receive_json()
        if not (isinstance( greeting, dict) or greeting.get("type") != CHAT_MESSAGE_TYPE.HELLO.value):
            await push_error_message(websocket, CHAT_ERROR_TYPE.INVALID_HELLO, close_after=True)
            return
        
        session_id = get_session_id(greeting.get(SESSION_ID_NAME))
        CHAT_MEMORY.setdefault(session_id, [])
        
        await push_system_message(websocket, CHAT_MESSAGE_TYPE.READY, session_id, "WebSocket connection established.")

        while True:
            try:
                event = await websocket.receive_json()
                msg_type = get_message_type(event.get('type'))
                
                if CHAT_MESSAGE_TYPE.PING == msg_type:
                    await push_system_message(websocket, CHAT_MESSAGE_TYPE.PING, session_id, 'pong')
                    continue
                
                if CHAT_MESSAGE_TYPE.USER_MESSAGE == msg_type:
                    await push_system_message(websocket, CHAT_MESSAGE_TYPE.SYSTEM_MESSAGE, session_id, event)
                    
                if CHAT_MESSAGE_TYPE.UNKNOWN == msg_type:
                    await push_error_message(websocket, CHAT_ERROR_TYPE.INVALID_TYPE)
                    continue

                user_message = (event.get("text") or "").strip()
                if not user_message:
                    continue # ignore empty user message
                
                reply = await build_response(user_message, session_id)
                CHAT_MEMORY[session_id].append(reply)

                await websocket.send_json({
                    "type": "assistant_message",
                    "message": reply,
                })
                
                await websocket.send_json({
                "type": "typing",
                "state": False,
                })
                
            except Exception as e:
                print(f"Error in WebSocket communication: {e}")
                break
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        
