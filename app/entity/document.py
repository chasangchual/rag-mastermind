from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, Text
from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from .base import ExternalBase


class Document(ExternalBase):
    __tablename__ = "documents"

    hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    extension: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    source: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    state: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    # Relationships
    embeddings: Mapped[list] = relationship(
        "Embedding",
        back_populates="document",
        cascade="all, delete-orphan",
        default_factory=list,
    )

    def __repr__(self):
        return f"<Document(id={self.id}, hash='{self.hash}', extension='{self.extension}')>"