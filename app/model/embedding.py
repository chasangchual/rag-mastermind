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
from app.model.document import Document

# pgvector HNSW supports regular vector only up to 2,000 dimensions;
# 3,072 would require halfvec or another indexing strategy.
# pgvector limits (https://github.com/pgvector/pgvector)
EMBEDDING_VECTOR_DIMENSIONS = 1536

class Embedding(ExternalBase):
    __tablename__ = "embedding"

    doc_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped [str] = mapped_column(Text, nullable=False)
    vector: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_VECTOR_DIMENSIONS), nullable=False
    )
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
