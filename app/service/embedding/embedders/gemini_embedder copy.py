from __future__ import annotations

from abc import ABC, abstractmethod

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.service.embedding.embedders.base_embedder import EmbeddingProvider
from app.model.embedding import EMBEDDING_VECTOR_DIMENSIONS
from langchain_qwen import QwenEmbeddings 

QWEN_EMBEDDING_MODEL = "text-embedding-qwen3-embedding-0.6b"
GEMMA_EMBEDDING_MODEL = "text-embedding-embeddinggemma-300m"

class GemmaEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self._embedder = GoogleGenerativeAIEmbeddings(
            model=TEXT_ONLY_EMBEDDING_MODEL,
            output_dimensionality=EMBEDDING_VECTOR_DIMENSIONS,
        )  # EMBEDDING_VECTOR_DIMENSIONS dimensions for Gemini embeddings

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._embedder.embed_documents(texts)
        return [list(vector) for vector in vectors]
