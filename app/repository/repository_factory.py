from dependency_injector import containers, providers
from app.repository.document_repository import DocumentRepository
from app.config.db import db_session

class RepositoryFactory(containers.DeclarativeContainer):
    config = providers
    document_repository = providers.Factory(DocumentRepository, db_session = db_session)