import dramatiq
from openai import max_retries
from app.service.embedding.splitters.splitter import EmbeddedChunk
from app.tasks.broker import rabbitmq_broker
from uuid import UUID, uuid4
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from typing import Optional
import logging

from app.repository.document_repository import DocumentRepository
from app.repository.repository_factory import RepositoryFactory
from app.config.db import db_session
from app.model.document import Document, DocumentStatus
from app.service.embedding.embedding_pipeline import build_default_pipeline
from app.service.embedding.embedders.gemini_embedder import GeminiEmbeddingProvider

@dramatiq.actor(
    queue_name="document_embedding",
    max_retries=3,
    min_backoff=10_000,
    max_backoff=300_000,
    time_limit=30 * 60 * 1000,
)
def embedding_document(
    public_id: UUID,
    document_path: str
) -> list[EmbeddedChunk]:
    embedding_pipeline = build_default_pipeline(embedder=GeminiEmbeddingProvider())
    try:
        embedded_chunks: list[EmbeddedChunk] = embedding_pipeline.process_document(public_id, document_path)
        # logging
        return embedded_chunks
    except Exception as ex:
        logging.error(ex)
        raise


@inject
@dramatiq.actor(
    queue_name="document_embedding",
    max_retries=3,
    min_backoff=10_000,
    max_backoff=300_000,
    time_limit=30 * 60 * 1000,
)
def process_document(
    document_id: UUID,
    db_session: db_session,
    document_repository: DocumentRepository = Depends(
        Provide[RepositoryFactory.document_repository]
    ),
):
    embedding_pipeline = build_default_pipeline(embedder=GeminiEmbeddingProvider())
    document: Optional[Document] = document_repository.find_by_public_id(document_id);
    
    if(document is None):
        return 

    if document.source is None:
        document_repository.update_State(document, DocumentStatus.FAILED, db_session)
        ex = ValueError(f"Document source is None for document_id: {document_id}. Cannot process document.")
        logging.error(ex)
        raise ex

    document_repository.update_State(document, DocumentStatus.PROGRESS, db_session)
    try:
        embedded_chunks: list[EmbeddedChunk] = embedding_pipeline.process_document(document_id, document.source)

        document.state = DocumentStatus.COMPLETED
        document_repository.update_State(document, DocumentStatus.COMPLETED, db_session)

    except Exception as ex:
        logging.error(ex)
        raise