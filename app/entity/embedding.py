from datetime import datetime, timezone
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy import String, Text
from sqlalchemy.orm import  Mapped, mapped_column

from .base import ExternalBase


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Embedding(ExternalBase):
    __tablename__ = "embeddings"

    doc_id: Mapped[Integer] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    index: Mapped[Integer] = mapped_column(Integer, nullable=False)
    text: Mapped [Text] = mapped_column(Text, nullable=False)
    vector: Mapped[Integer]= mapped_column(
        Vector(1536), nullable=False
    )  # 1536 dimensions for OpenAI embeddings
    meta: Mapped[Integer]= mapped_column(JSON, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="embeddings")

    def __repr__(self):
        return f"<Embedding(id={self.id}, doc_id={self.doc_id}, index={self.index})>"