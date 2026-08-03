from __future__ import annotations

import logging

from app.model.lms import call_with_reconnect
from app.service.embedding.embedders.base_embedder import EmbeddingProvider

QWEN_EMBEDDING_8B_MODEL = "text-embedding-qwen3-embedding-8b"


class LMStudioEmbeddingProvider(EmbeddingProvider):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            return call_with_reconnect(
                lambda client: [
                    list(vector)
                    for vector in client.embedding.model(QWEN_EMBEDDING_8B_MODEL).embed(texts)
                ]
            )
        except Exception as e:
            logging.error(f"Failed to embed texts: {e}")
            return []
