from shutil import unregister_archive_format

from fastapi import APIRouter, Request, Cookie, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from typing import Any, Optional
import secrets
from enum import Enum
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, timezone

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

NONCE_LENGTH = 16
PAGES = {
    "chat": {
        "title": "Chat",
        "subtitle": "Ask questions over the indexed document library.",
        "template": "pages/chat.html",
    },
    "documents": {
        "title": "Documents",
        "subtitle": "Upload, parse, chunk, and manage source files.",
        "template": "pages/documents.html",
    },
    "embeddings": {
        "title": "Embeddings",
        "subtitle": "Configure chunking, embedding, vector index, and retrieval settings.",
        "template": "pages/embeddings.html",
    },
    "settings": {
        "title": "Settings",
        "subtitle": "Manage application, model, and UI preferences.",
        "template": "pages/settings.html",
    },
    "logs": {
        "title": "Logs",
        "subtitle": "Monitor ingestion, embedding, retrieval, and chat activity.",
        "template": "pages/logs.html",
    },
}

DEFAULT_ASSISTANT_MESSAGE = (
    "This is a placeholder WebSocket response from FastAPI. "
    "The RAG pipeline is not connected yet. Later, this handler can call your "
    "retriever, embedding/vector store, reranker, and LLM service."
)

CHAT_MEMORY: dict[str, list[dict[str, Any]]] = {}
templates = Jinja2Templates(directory="app/templates")

home_router = APIRouter(
    prefix="/app"
)

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_session_id(raw_session_id) -> str:
    if isinstance(raw_session_id, str) and raw_session_id.strip():
        return SessionUtils.get_or_create_session_id(raw_session_id.strip())
    return SessionUtils.get_or_create_session_id(None)

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
    
@home_router.get("/", response_class=RedirectResponse)
async def app_root(request: Request):
    redirect_url = request.url_for("app_page", page="chat")
    return RedirectResponse(url=redirect_url)

@home_router.get("/{page}", response_class=HTMLResponse, name="app_page")
async def app_page(
    request: Request,
    page: str,
    session_id: Optional[str] = Cookie(default=None, alias=SESSION_ID_NAME),
):
    if page not in PAGES:
        redirect_url = request.url_for("app_page", page="chat")
        return RedirectResponse(url=redirect_url)

    sid = SessionUtils.get_or_create_session_id(session_id)

    page_meta = PAGES[page]

    params = {
        "request": request,
        "session_id": sid,
        "nonce": secrets.token_urlsafe(NONCE_LENGTH),

        "app_title": "Mastermind RAG Chat Studio",

        # Current page key: chat, documents, embeddings, settings, logs
        "page": page,

        # Keep this because your templates are using page_meta
        "page_meta": page_meta,

        # These are also convenient for topbar/base templates
        "page_title": page_meta["title"],
        "page_subtitle": page_meta["subtitle"],
        "page_template": page_meta["template"],

        # Used by sidebar
        "pages": PAGES,
    }

    return templates.TemplateResponse(
        request,
        "base.html",
        params,
    )
    
@home_router.websocket("/ws")
async def ws_chat(websocket: WebSocket):
    """Chat WebSocket endpoint.
    Protocol:
    1. Client connects to /app/ws.
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
        
