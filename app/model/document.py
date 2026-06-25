from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Enum
from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
import enum

from .base import ExternalBase

if TYPE_CHECKING:
    from app.model.embedding import Embedding

class DocumentStatus(enum.Enum):
    PENDING = 'pending',
    PROGRESS = 'progress',
    PAUSED = 'paused',
    CANCELED = 'canceled',
    COMPLETED = 'completed',
    FAILED = 'failed',

class Document(ExternalBase):
    __tablename__ = "document"

    hash: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    extension: Mapped[str | None] = mapped_column(String(50), nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    source: Mapped[str | None] = mapped_column(String(500), nullable=False, default=None)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    state: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus, name = 'state'), default=DocumentStatus.PENDING, nullable=False)

    
    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding",
        back_populates="document",
        cascade="all, delete-orphan",
        default_factory=list,
    )

    def __repr__(self):
        return f"<Document(id={self.id}, hash='{self.hash}', extension='{self.extension}')>"
