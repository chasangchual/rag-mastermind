from typing import Any, Generator, Annotated

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

from app.config.app_config import get_config

# Load application configuration and extract the database URL
config = get_config()
DATABASE_URL = config.database_url

# Initialize the SQLAlchemy engine to manage database connections
# echo=False disables SQL logging to the console for cleaner production logs
engine = create_engine(DATABASE_URL, echo=config.sql_logging)

# Create a configured "Session" class factory
# autocommit=False ensures transactions are explicitly committed
# autoflush=False prevents automatic flushing of changes before queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency that yields a database session.
    Ensures that the session is properly closed after the request lifecycle,
    even if an exception occurs during processing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Generator[Session, Any, None]:
    """
    A type-hinted generator function that yields an independent database session.
    Acts as the underlying callable for the FastAPI dependency injection.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# A reusable type alias for FastAPI endpoint dependency injection.
# Instead of writing `db: Session = Depends(get_session)` in every route, you can simply write `db: db_session`.
db_session = Annotated[Session, Depends(get_session)]