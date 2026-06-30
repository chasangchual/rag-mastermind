from __future__ import annotations

from typing import TYPE_CHECKING

from typing import Optional, Dict, Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import ExternalBase

if TYPE_CHECKING:
    from app.model.document import Document

class Embedding(ExternalBase):
    __tablename__ = "embedding"

    doc_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    index: Mapped[int] = mapped_column(Integer, nullable=True)
    text: Mapped [str] = mapped_column(Text, nullable=True)
    vector: Mapped[Vector]= mapped_column(
        Vector(1536), nullable=True
    )  # 1536 dimensions for OpenAI embeddings
    meta: Mapped[Optional[Dict[str, Any]]]= mapped_column(JSON, nullable=True)

    # Relationships
    document: Mapped[Document] = relationship(Document, back_populates="embeddings")

    __table_args__ = (
        Index(
            "idx_embedding_vector",
            "vector",
            postgresql_using="hnsw",
            postgresql_ops={"vector": "vector_cosine_ops"}, # Or vector_l2_ops / vector_ip_ops
        ),
    )

    def __repr__(self) -> str:
        # Safely get id if it's auto-generated post-insertion
        id_val = getattr(self, "id", "None")
        return f"<Embedding(id={id_val}, doc_id={self.doc_id}, index={self.index})>"
