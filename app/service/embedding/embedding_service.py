import logging
from typing import Optional
import uuid
from xml.dom.minidom import Document

from dependency_injector.wiring import inject
from sqlalchemy import UUID

from app.model.document import Document, DocumentStatus
from app.model.embedding import Embedding
from app.config.db import db_session
from app.repository.document_repository import DocumentRepository
from app.repository.embedding_repository import EmbeddingRepository
from app.repository.qdrant_repository import QdrantRepository
from app.repository.repository_factory import RepositoryFactory
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from app.service.embedding.embedders.lmstudio_embedder import LMStudioEmbeddingProvider
from app.service.embedding.embedding_pipeline import default_pipeline
from app.service.embedding.splitters.splitter import EmbeddedChunk

class EmbeddingService:
    def __init__(self) -> None:
        pass

    def run_embedding(
        self,
        document_public_id: UUID,
        db_session: db_session,
        document_repository: DocumentRepository,
        embedding_repository: QdrantRepository,
    ) -> bool:

        document: Optional[Document] = document_repository.find_by_public_id(
            document_public_id, db_session=db_session
        )

        if document is None:
            return False

        if document.source is None:
            document_repository.update_State(document, DocumentStatus.FAILED, db_session)
            ex = ValueError(
                f"Document source is None for document_id: {document_public_id}. Cannot process document."
            )
            logging.error(ex)
            raise ex

        document_repository.update_State(document, DocumentStatus.PROGRESS, db_session)
        try:
            # embedding_document.send(document.source)
            embedded_chunks: list[EmbeddedChunk] = default_pipeline.process_document(
                document_public_id, document.source
            )

            embedding_repository.add(document_public_id, embedded_chunks)

            document_repository.update_State(document, DocumentStatus.COMPLETED, db_session)
            return True
        except Exception as ex:
            document_repository.update_State(document, DocumentStatus.FAILED, db_session)
            logging.error(ex)
            raise
        
embedding_service = EmbeddingService()