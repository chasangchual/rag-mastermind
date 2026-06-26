from typing import Optional

from sqlalchemy.orm import Session
from app.config.db import db_session


class RepositoryBase:
    """
    Base repository class providing shared database session management
    for data access layers.
    """

    def __init__(self, db_session=None):
        """
        Initializes the repository with an optional SQLAlchemy session.
        """
        self.session = db_session

    def set_session(self, db_session: db_session):
        """
        Explicitly sets or overrides the current database session.

        Note: Use the standard SQLAlchemy `Session` for type hinting here,
        rather than the FastAPI `db_session` dependency alias.
        """
        self.session = db_session

    def _get_session(self, db_session: Optional[Session] = None) -> Session:
        """
        Internal helper to resolve which session to use for a query.
        Prioritizes a locally passed session over the instance's session.

        Raises:
            ValueError: If no session is provided or currently set.
        """
        # 1. Prioritize the method-level session if explicitly passed
        if db_session is not None:
            return db_session

        # 2. Fall back to the instance-level session if available
        if self.session is not None:
            return self.session

        # 3. Raise a clean exception if everything is missing
        raise ValueError(
            "Database session is missing. Pass a session to the method "
            "or initialize the repository with one."
        )
