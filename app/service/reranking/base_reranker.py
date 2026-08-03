from __future__ import annotations

from abc import ABC, abstractmethod

from langchain_core.documents import Document

class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, documents: list[Document]) -> list[tuple[Document, float]]:
        raise NotImplementedError