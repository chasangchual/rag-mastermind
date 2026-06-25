from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass


class AuditableBase(MappedAsDataclass, DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    __abstract__ = True

    # init=False tells Python NOT to include this in the constructor, since the DB generates it automatically via autoincrement.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, init=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("now()"),
        nullable=False,
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("now()"),
        nullable=False,
        init=False,
    )


class ExternalBase(AuditableBase):
    __abstract__ = True
    public_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), unique=True, index=True, default=uuid4, nullable=False, kw_only=True)
