from typing import List, Optional
from uuid import UUID

from app.repository.base_repository import RepositoryBase
from app.config.db import db_session
from app.model.document import Document

class DocumentRepository(RepositoryBase):
    def __init__(self, db_session=None):
        super().__init__(db_session)

    def find_all(self, session: db_session) -> List[Document]:
        return self._get_session(session).query(Document).all()

    def find_by_public_id(self, public_id: UUID, session: db_session) -> Optional[Document]:
        return self._get_session(session).query(Document).filter(Document.public_id == public_id).first()

    def add(self, document: Document, session: db_session) -> Optional[Document]:
        self._get_session(session).add(document)
        self._get_session(session).commit()
        self._get_session(session).refresh(document)
        return document

    def update(self, document: Document, session: db_session) -> Optional[Document]:
        self._get_session(session).add(document)
        self._get_session(session).commit()
        self._get_session(session).refresh(document)
        return document

    def delete_by_public_id(self, public_id: UUID, session: db_session) -> bool:
        doc = self._get_session(session).query(Document).filter(Document.public_id == public_id).first()
        if doc:
            self._get_session(session).delete(doc)
            self._get_session(session).commit()
            return True
        return False