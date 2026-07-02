from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic lightweight embedding useful for local testing."""

    def __init__(self, dimensions: int = 128) -> None:
        self._dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            repeats = (self._dimensions + len(digest) - 1) // len(digest)
            expanded = (digest * repeats)[: self._dimensions]
            vectors.append([byte / 255.0 for byte in expanded])
        return vectors