import uuid
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.model.document import Document


class DocumentRequestModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(default_factory=uuid.uuid4)
    hash: str
    extension: str
    text: str | None = None
    source: str | None = None
    meta: dict | None = None
    state: str = "pending"

    @classmethod
    def from_entity(cls, document: Document) -> "DocumentRequestModel":
        return cls(
            public_id=document.public_id,
            hash=document.hash,
            extension=document.extension,
            text=document.text,
            source=document.source,
            meta=document.meta,
            state=document.state,
        )
