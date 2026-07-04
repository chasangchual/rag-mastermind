import logging

from typing import List, Optional
from uuid import UUID

from app.repository.base_repository import RepositoryBase
from app.config.db import db_session
from app.model.document import Document, DocumentStatus
from sqlalchemy.orm import Session

class DocumentRepository(RepositoryBase):
    def __init__(self, db_session=None):
        super().__init__(db_session)

    def find_all(self, db_session: Optional[Session] = None) -> List[Document]:
        try:
            return self._get_session(db_session).query(Document).all()
        except Exception as ex:
            logging.error(f"Failed to find all documents. Error: {ex}")
            raise ex

    def find_by_public_id(self, public_id: UUID, db_session: Optional[Session] = None) -> Optional[Document]:
        try:
            return self._get_session(db_session).query(Document).filter(Document.public_id == public_id).first()
        except Exception as ex:
            logging.error(f"Failed to find document by public_id: {public_id}. Error: {ex}")
            raise ex

    def find_all_by_state(self, state: DocumentStatus, db_session: Optional[Session] = None) -> List[Document]:
        try:
            return self._get_session(db_session).query(Document).filter(Document.state == state).all()
        except Exception as ex:
            logging.error(f"Failed to find documents by state {state}. Error: {ex}")
            raise ex

    def add(self, document: Document, db_session: Optional[Session] = None) -> Optional[Document]:
        try:
            self._get_session(db_session).add(document)
            self._get_session(db_session).commit()
            self._get_session(db_session).refresh(document)
            return document
        except Exception as ex:
            logging.error(f"Failed to add document for document_id: {document.id}. Error: {ex}")
            raise ex

    def update(self, document: Document, db_session: Optional[Session] = None) -> Optional[Document]:
        try:
            self._get_session(db_session).merge(document)
            self._get_session(db_session).commit()
            self._get_session(db_session).refresh(document)
            return document
        except Exception as ex:
            logging.error(f"Failed to update document for document_id: {document.id}. Error: {ex}")
            raise ex

    def delete_by_public_id(self, public_id: UUID, db_session: Optional[Session] = None) -> bool:
        try:
            doc = self._get_session(db_session).query(Document).filter(Document.public_id == public_id).first()
            if doc:
                self._get_session(db_session).delete(doc)
                self._get_session(db_session).commit()
                return True
            return False
        except Exception as ex:
            logging.error(f"Failed to delete document for public_id: {public_id}. Error: {ex}")
            raise ex

    def update_State(self, document: Document, state: DocumentStatus, db_session: Optional[Session] = None) -> Optional[Document]:
        try:
            document.state = state
            self.update(document, db_session=db_session)
        except Exception as ex:
            logging.error(f"Failed to update document state for document_id: {document.id}. Error: {ex}")
            raise ex

    def update_state_public_id(self, public_id: UUID, state: DocumentStatus, db_session: Optional[Session] = None) -> Optional[Document]:
        try:
            document = self.find_by_public_id(public_id, db_session=db_session)
            if document:
                document.state = state
                self._get_session(db_session).commit()
                self._get_session(db_session).refresh(document)
            return document
        except Exception as ex:
            logging.error(f"Failed to update document state for public_id: {public_id}. Error: {ex}")
            raise ex
