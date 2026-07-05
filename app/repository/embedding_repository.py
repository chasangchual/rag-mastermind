import logging

from typing import List, Optional
from uuid import UUID

from app.model.embedding import Embedding
from app.repository.base_repository import RepositoryBase
from app.model.document import Document
from sqlalchemy.orm import Session

class EmbeddingRepository(RepositoryBase):
    def __init__(self, db_session=None):
        super().__init__(db_session)

    def find_all(self, db_session: Optional[Session] = None) -> List[Embedding]:
        try:
            return self._get_session(db_session).query(Embedding).all()
        except Exception as ex:
            logging.error(f"Failed to find all embeddings. Error: {ex}")
            raise ex

    def find_by_public_id(self, public_id: UUID, db_session: Optional[Session] = None) -> Optional[Embedding]:
        try:
            return self._get_session(db_session).query(Embedding).filter(Embedding.public_id == public_id).first()
        except Exception as ex:
            logging.error(f"Failed to find embedding by public_id: {public_id}. Error: {ex}")
            raise ex

    def find_all_by_document(self, document: Document, db_session: Optional[Session] = None) -> List[Embedding]:
        try:
            return self._get_session(db_session).query(Embedding).filter(Embedding.doc_id == document.id).all()
        except Exception as ex:
            logging.error(f"Failed to find embeddings by document: {document.id}. Error: {ex}")
            raise ex

    def add(self, embedding: Embedding, db_session: Optional[Session] = None) -> Optional[Embedding]:
        session = self._get_session(db_session)
        document_id = embedding.doc_id
        try:
            session.add(embedding)
            session.commit()
            session.refresh(embedding)
            return embedding
        except Exception:
            session.rollback()
            logging.exception(
                "Failed to add embedding for document_id: %s", document_id
            )
            raise

    def update(self, embedding: Embedding, db_session: Optional[Session] = None) -> Optional[Embedding]:
        session = self._get_session(db_session)
        document_id = embedding.doc_id
        try:
            merged_embedding = session.merge(embedding)
            session.commit()
            session.refresh(merged_embedding)
            return merged_embedding
        except Exception:
            session.rollback()
            logging.exception(
                "Failed to update embedding for document_id: %s", document_id
            )
            raise

    def delete_by_public_id(self, public_id: UUID, db_session: Optional[Session] = None) -> bool:
        session = self._get_session(db_session)
        try:
            embedding = (
                session.query(Embedding)
                .filter(Embedding.public_id == public_id)
                .first()
            )
            if embedding:
                session.delete(embedding)
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            logging.exception(
                "Failed to delete embedding for public_id: %s", public_id
            )
            raise
