from fastapi import APIRouter, Request, Cookie, WebSocket, WebSocketDisconnect, Depends
from dependency_injector.wiring import inject, Provide
from typing import Any, Optional, List
import secrets
from enum import Enum
from fastapi.responses import HTMLResponse, RedirectResponse
from app.config.db import db_session
from app.repository.repository_factory import RepositoryFactory
from app.utils.session_util import SESSION_ID_NAME, SessionUtils
from app.repository.document_repository import DocumentRepository

documents_router = APIRouter(
    prefix="/app/documents"
)

@documents_router.get("", status_code=200, response_class=HTMLResponse)
@inject
async def get_documents(request: Request, 
                        db_session: db_session, 
                        session_id: Optional[str] = Cookie(None),
                        document_repository: DocumentRepository = Depends(Provide[RepositoryFactory.document_repository])) -> List[Any]:
    """
    Endpoint to retrieve and display all documents.
    
    Args:
        request (Request): The incoming HTTP request.
        session_id (Optional[str]): The session ID from cookies, if present.
        document_repository (DocumentRepository): Injected repository for document operations.
    """
    return document_repository.find_all(session=db_session)