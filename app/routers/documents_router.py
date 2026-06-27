import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

from app.config.app_config import get_config
from app.config.db import db_session
from app.model.document import Document, DocumentStatus
from app.repository.document_repository import DocumentRepository
from app.repository.repository_factory import RepositoryFactory
from app.routers.dto.document_dto import DocumentResponse, NewDocumentRequest
from dependency_injector.wiring import inject, Provide

from starlette import status

documents_router = APIRouter(prefix="/app/api/documents")


def text_from_upload(
    filename: str, content_type: str | None, content: bytes
) -> str | None:
    extension = Path(filename).suffix.lower()
    text_extensions = {
        ".csv",
        ".html",
        ".htm",
        ".json",
        ".md",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }

    if (
        content_type and content_type.startswith("text/")
    ) or extension in text_extensions:
        return content.decode("utf-8", errors="replace")

    return None


def save_upload_file(filename: str, content: bytes) -> Path:
    upload_dir = get_config().working_directory / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    storage_name = f"{uuid.uuid4()}_{Path(filename).name}"
    local_path = upload_dir / storage_name
    local_path.write_bytes(content)
    return local_path


async def document_from_upload(file: UploadFile) -> Document:
    content = await file.read()
    filename = Path(file.filename or "uploaded-file").name
    extension = Path(filename).suffix.lower().lstrip(".") or ""
    local_path = save_upload_file(filename, content)

    return Document(
        public_id=uuid.uuid4(),
        hash=hashlib.sha256(content).hexdigest(),
        extension=extension,
        text=text_from_upload(filename, file.content_type, content),
        source=str(local_path),
        meta={
            "filename": filename,
            "content_type": file.content_type,
            "size": len(content),
            "local_path": str(local_path),
        },
        state=DocumentStatus.PENDING,
    )


@documents_router.get("", status_code=200, response_model=list[DocumentResponse])
@inject
async def get_documents(
    db_session: db_session,
    document_repository: DocumentRepository = Depends(Provide[RepositoryFactory.document_repository]),
) -> list[DocumentResponse]:
    """
    Endpoint to retrieve and display all documents.

    Args:
        document_repository (DocumentRepository): Injected repository for document operations.
    """
    documents = document_repository.find_all(db_session=db_session)
    return [DocumentResponse.from_entity(document) for document in documents]


@documents_router.post("", status_code=201, response_model=DocumentResponse)
@inject
async def create_document(
    request: NewDocumentRequest,
    db_session: db_session,
    document_repository: DocumentRepository = Depends(
        Provide[RepositoryFactory.document_repository]
    ),
) -> DocumentResponse:
    document = document_repository.add(request.to_entity(), db_session=db_session)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"failed to create a new document with [{request.source}] not found",
        )
    return DocumentResponse.from_entity(document)


@documents_router.post(
    "/upload", status_code=201, response_model=list[DocumentResponse]
)
@inject
async def upload_documents(
    db_session: db_session,
    files: list[UploadFile] = File(...),
    document_repository: DocumentRepository = Depends(
        Provide[RepositoryFactory.document_repository]
    ),
) -> list[DocumentResponse]:
    documents = []

    for file in files:
        document = await document_from_upload(file)
        documents.append(document_repository.add(document, db_session=db_session))

    return [DocumentResponse.from_entity(document) for document in documents]
