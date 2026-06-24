from fastapi import APIRouter, Depends

from app.config.db import db_session
from app.repository.document_repository import DocumentRepository
from app.routers.dto.document_dto import DocumentRequestModel

documents_router = APIRouter(
    prefix="/app/api/documents"
)


def get_document_repository() -> DocumentRepository:
    return DocumentRepository()


@documents_router.get("", status_code=200, response_model=list[DocumentRequestModel])
async def get_documents(
    db_session: db_session,
    document_repository: DocumentRepository = Depends(get_document_repository),
) -> list[DocumentRequestModel]:
    """
    Endpoint to retrieve and display all documents.
    
    Args:
        document_repository (DocumentRepository): Injected repository for document operations.
    """
    documents = document_repository.find_all(session=db_session)
    return [DocumentRequestModel.from_entity(document) for document in documents]
