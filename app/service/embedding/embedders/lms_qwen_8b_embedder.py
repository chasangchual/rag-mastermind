from __future__ import annotations

import logging

from app.model.lms import lms_default_client
from app.service.embedding.embedders.base_embedder import EmbeddingProvider

QWEN_EMBEDDING_8B_MODEL = "text-embedding-qwen3-embedding-8b"


class LMStudioEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        try:
            self._embedder = lms_default_client.embedding.model(QWEN_EMBEDDING_8B_MODEL)
        except Exception as e:
            logging.error(f"Failed to initialize LMStudioEmbeddingProvider: {e}")
            

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        try:
            if not texts:
                return []
            return [list(vector) for vector in self._embedder.embed(texts)]
        except Exception as e:
            logging.error(f"Failed to embed texts: {e}")
            return []
