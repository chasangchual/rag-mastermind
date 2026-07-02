from __future__ import annotations

from abc import ABC, abstractmethod

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.service.embedding.embedders.base_embedder import EmbeddingProvider

class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str = "embeddinggemma:300m", base_url: str | None = None) -> None:
        self._embedder = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")


    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._embedder.embed_documents(texts)
        return [list(vector) for vector in vectors]
