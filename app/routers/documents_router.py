import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from app.config.db import db_session
from app.model.document import Document
from app.repository.document_repository import DocumentRepository
from app.routers.dto.document_dto import DocumentResponse, NewDocumentRequest

documents_router = APIRouter(
    prefix="/app/api/documents"
)


def get_document_repository() -> DocumentRepository:
    return DocumentRepository()


def text_from_upload(filename: str, content_type: str | None, content: bytes) -> str | None:
    extension = Path(filename).suffix.lower()
    text_extensions = {".csv", ".html", ".htm", ".json", ".md", ".txt", ".xml", ".yaml", ".yml"}

    if (content_type and content_type.startswith("text/")) or extension in text_extensions:
        return content.decode("utf-8", errors="replace")

    return None


async def document_from_upload(file: UploadFile) -> Document:
    content = await file.read()
    filename = Path(file.filename or "uploaded-file").name
    extension = Path(filename).suffix.lower().lstrip(".") or None

    return Document(
        public_id=uuid.uuid4(),
        hash=hashlib.sha256(content).hexdigest(),
        extension=extension,
        text=text_from_upload(filename, file.content_type, content),
        source=filename,
        meta={
            "filename": filename,
            "content_type": file.content_type,
            "size": len(content),
        },
        state="uploaded",
    )


@documents_router.get("", status_code=200, response_model=list[DocumentResponse])
async def get_documents(
    db_session: db_session,
    document_repository: DocumentRepository = Depends(get_document_repository),
) -> list[DocumentResponse]:
    """
    Endpoint to retrieve and display all documents.
    
    Args:
        document_repository (DocumentRepository): Injected repository for document operations.
    """
    documents = document_repository.find_all(session=db_session)
    return [DocumentResponse.from_entity(document) for document in documents]


@documents_router.post("", status_code=201, response_model=DocumentResponse)
async def create_document(
    request: NewDocumentRequest,
    db_session: db_session,
    document_repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentResponse:
    document = document_repository.add(request.to_entity(), session=db_session)
    return DocumentResponse.from_entity(document)


@documents_router.post("/upload", status_code=201, response_model=list[DocumentResponse])
async def upload_documents(
    db_session: db_session,
    files: list[UploadFile] = File(...),
    document_repository: DocumentRepository = Depends(get_document_repository),
) -> list[DocumentResponse]:
    documents = []

    for file in files:
        document = await document_from_upload(file)
        documents.append(document_repository.add(document, session=db_session))

    return [DocumentResponse.from_entity(document) for document in documents]
