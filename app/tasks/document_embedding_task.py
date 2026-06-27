import dramatiq
from openai import max_retries
from app.tasks.broker import rabbitmq_broker
from uuid import UUID, uuid4
from dependency_injector.wiring import inject, Provide
from fastapi import Depends

from app.repository.document_repository import DocumentRepository
from app.repository.repository_factory import RepositoryFactory
from app.config.db import db_session
from app.model.document import Document, DocumentStatus
from typing import Optional

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
    document: Optional[Document] = document_repository.find_by_public_id(document_id);
    
    if(document is None):
        return 
    try:    
        document.state = DocumentStatus.PROGRESS
        document_repository.update(document, db_session)
    except Exception as ex:
         raise   

    try:
        text = extract_text(document.storage_path)
        chunks = split_text(text, chunk_size=1000, overlap=150)

        for batch in batched(chunks, 64):
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch,
            )
            vectors = [item.embedding for item in response.data]
            save_document_chunks(document_id, batch, vectors)

        document.state = DocumentStatus.COMPLETED
        document_repository.update(document, db_session)

    except Exception as ex:
        document.state = DocumentStatus.FAILED
        document_repository.update(document, db_session)
        raise
