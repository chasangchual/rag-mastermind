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
        return self._get_session(db_session).query(Document).all()

    def find_by_public_id(self, public_id: UUID, db_session: Optional[Session] = None) -> Optional[Document]:
        return self._get_session(db_session).query(Document).filter(Document.public_id == public_id).first()

    def find_all_by_state(self, state: DocumentStatus, db_session: Optional[Session] = None) -> List[Document]:
        return self._get_session(db_session).query(Document).filter(Document.state == state).all()

    def add(self, document: Document, db_session: Optional[Session] = None) -> Optional[Document]:
        self._get_session(db_session).add(document)
        self._get_session(db_session).commit()
        self._get_session(db_session).refresh(document)
        return document

    def update(self, document: Document, db_session: Optional[Session] = None) -> Optional[Document]:
        self._get_session(db_session).add(document)
        self._get_session(db_session).commit()
        self._get_session(db_session).refresh(document)
        return document

    def delete_by_public_id(self, public_id: UUID, db_session: Optional[Session] = None) -> bool:
        doc = self._get_session(db_session).query(Document).filter(Document.public_id == public_id).first()
        if doc:
            self._get_session(db_session).delete(doc)
            self._get_session(db_session).commit()
            return True
        return False
