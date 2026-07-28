from __future__ import annotations

from app.model.lms import lms_default_client
from app.service.embedding.embedders.base_embedder import EmbeddingProvider

QWEN_EMBEDDING_8B_MODEL = "text-embedding-qwen3-embedding-8b"


class LMStudioEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self._embedder = lms_default_client.embedding.model(QWEN_EMBEDDING_8B_MODEL)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [list(vector) for vector in self._embedder.embed(texts)]
