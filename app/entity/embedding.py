from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy import String, Text, Index
from sqlalchemy.orm import  Mapped, mapped_column

from .base import ExternalBase
from app.entity.document import Document

def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


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
    vector: Mapped[Vector]= mapped_column(
        Vector(1536), nullable=False
    )  # 1536 dimensions for OpenAI embeddings
    meta: Mapped[Optional[Dict[str, Any]]]= mapped_column(JSON, nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="embedding")

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
