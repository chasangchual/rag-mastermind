from dependency_injector import containers, providers
from app.repository.document_repository import DocumentRepository
from app.repository.embedding_repository import EmbeddingRepository
from app.repository.qdrant_repository import QdrantRepository
from app.config.db import db_session

class RepositoryFactory(containers.DeclarativeContainer):
    config = providers
    document_repository = providers.Factory(DocumentRepository)
    embedding_repository = providers.Factory(EmbeddingRepository)
    qdrant_repository = providers.Factory(QdrantRepository)