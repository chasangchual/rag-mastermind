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

documents_router = APIRouter(
    prefix="/app/documents"
)