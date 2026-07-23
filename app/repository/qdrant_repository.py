import logging

from typing import Optional
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    ScoredPoint,
    VectorParams,
)

from app.config.app_config import get_config
from app.config.qdrant import client as default_client
from app.service.embedding.splitters.splitter import EmbeddedChunk

config = get_config()


class QdrantRepository:
    def __init__(self, client: Optional[QdrantClient] = None):
        self.client = client or default_client
        self.collection_name = config.qdrant_collection_name
        self.dense_vector_name = config.qdrant_dense_vector

    def ensure_collection(self) -> None:
        """
        Creates the collection if it doesn't already exist, per Qdrant.md.
        """
        try:
            if not self.client.collection_exists(self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        self.dense_vector_name: VectorParams(
                            size=config.qdrant_vector_size,
                            distance=Distance(config.qdrant_distance_metric),
                        )
                    },
                )
        except Exception as ex:
            logging.error(f"Failed to ensure Qdrant collection {self.collection_name}. Error: {ex}")
            raise

    def add(self, document_id: UUID, embedded_chunks: list[EmbeddedChunk]) -> list[str]:
        """
        Upserts one point per chunk, keyed by the chunk's own id.
        """
        if not embedded_chunks:
            return []

        points = [
            PointStruct(
                id=embedded_chunk.chunk.id,
                vector={self.dense_vector_name: embedded_chunk.vector},
                payload={
                    "document_id": str(document_id),
                    "chunk_index": embedded_chunk.chunk.index,
                    "text": embedded_chunk.chunk.text,
                    **embedded_chunk.chunk.metadata,
                },
            )
            for embedded_chunk in embedded_chunks
        ]

        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
            return [point.id for point in points]
        except Exception as ex:
            logging.error(f"Failed to upsert Qdrant points for document_id: {document_id}. Error: {ex}")
            raise

    def delete_by_document_id(self, document_id: UUID) -> None:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[FieldCondition(key="document_id", match=MatchValue(value=str(document_id)))]
                ),
            )
        except Exception as ex:
            logging.error(f"Failed to delete Qdrant points for document_id: {document_id}. Error: {ex}")
            raise

    def search(self, vector: list[float], limit: int = 5) -> list[ScoredPoint]:
        try:
            return self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                using=self.dense_vector_name,
                limit=limit,
            ).points
        except Exception as ex:
            logging.error(f"Failed to search Qdrant collection {self.collection_name}. Error: {ex}")
            raise
