from xml.dom.minidom import Document

from dependency_injector.wiring import inject

from app.model.document import Document, DocumentStatus
from app.model.embedding import Embedding
from app.config.db import db_session
from app.repository.document_repository import DocumentRepository
from app.repository.repository_factory import RepositoryFactory
from dependency_injector.wiring import inject, Provide
from fastapi import Depends


class EmbeddingService:
    def __init__(self) -> None:
        pass

    @inject
    def run_embedding(
        self,
        db_session: db_session,
        document_repository: DocumentRepository = Depends(Provide[RepositoryFactory.document_repository]),
    ):
        documents = document_repository.find_all_by_state(
            DocumentStatus.PENDING, db_session=db_session
        )
