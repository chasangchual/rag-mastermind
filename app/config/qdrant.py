from typing import Annotated

from fastapi import Depends
from qdrant_client import QdrantClient

from app.config.app_config import get_config

config = get_config()

# Single shared client for the process; QdrantClient is thread-safe for reuse.
client = QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key)


def get_qdrant_client() -> QdrantClient:
    """
    FastAPI dependency that yields the shared Qdrant client.
    """
    return client


# Reusable type alias, mirroring `db_session` in app/config/db.py.
qdrant_client = Annotated[QdrantClient, Depends(get_qdrant_client)]
