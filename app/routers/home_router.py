from shutil import unregister_archive_format

from fastapi import APIRouter, Request, Cookie, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from typing import Any, Optional
import secrets
from enum import Enum
from fastapi.responses import HTMLResponse, RedirectResponse

from app.utils.session_util import SESSION_ID_NAME, SessionUtils, get_session_id
from app.utils.date_util import now_utc_iso

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

templates = Jinja2Templates(directory="app/templates")

home_router = APIRouter(
    prefix="/app"
)

    
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

        # These are also convenient for top bar/base templates
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
