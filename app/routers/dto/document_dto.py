import uuid
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.model.document import Document, DocumentStatus

class NewDocumentRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: str

    def to_entity(self) -> Document:
        return Document(
            public_id=uuid.uuid4(),
            hash=None,
            extension=None,
            text=None,
            source=self.source,
            meta=None,
            state=DocumentStatus.PENDING,
        )


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(default_factory=uuid.uuid4)
    hash: str | None = None
    extension: str | None = None
    text: str | None = None
    source: str | None = None
    meta: dict | None = None
    state: DocumentStatus = DocumentStatus.PENDING

    @classmethod
    def from_entity(cls, document: Document) -> "DocumentResponse":
        return cls(
            public_id=document.public_id,
            hash=document.hash,
            extension=document.extension,
            text=document.text,
            source=document.source,
            meta=document.meta,
            state=document.state,
        )
