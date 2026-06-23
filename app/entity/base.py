from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy import Column, DateTime, Integer
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass

def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)

class AuditableBase(MappedAsDataclass, DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    __abstract__ = True

    # init=False tells Python NOT to include this in the constructor, since the DB generates it automatically via autoincrement.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, init=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, kw_only=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False, kw_only=True)


class ExternalBase(AuditableBase):
    __abstract__ = True
    public_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), unique=True, index=True, default=uuid4, nullable=False, kw_only=True)
    