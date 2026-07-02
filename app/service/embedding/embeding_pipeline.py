from __future__ import annotations

from app.service.embedding.loaders.base_loader import ContentSourceLoaderRegistry
from app.service.embedding.splitters.splitter import DocumentSplitter, EmbeddedChunk, Chunk
from app.service.embedding.embedders.base_embedder import EmbeddingProvider
from dataclasses import dataclass, field


@dataclass(slots=True)
class PipelineConfig:
    recursive: bool = True
    chunk_size: int = 1200
    chunk_overlap: int = 200
    embedding_batch_size: int = 32
    text_encoding: str = "utf-8"
    supported_extensions: set[str] = field(
        default_factory=lambda: {
            ".txt",
            ".md",
            ".rst",
            ".pdf",
            ".docx",
            ".doc",
            ".xlsx",
            ".xls",
            ".pptx",
            ".ppt",
        }
    )


class EmbeddingPipeline:
    def __init__(
        self,
        registry: ContentSourceLoaderRegistry,
        splitter: DocumentSplitter,
        embedder: EmbeddingProvider,
        config: PipelineConfig | None = None,
    ) -> None:
        self._registry = registry
        self._splitter = splitter
        self._embedder = embedder
        self._config = config or PipelineConfig()
    def _embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        if not chunks:
            return []

        embedded: list[EmbeddedChunk] = []
        batch_size = self._config.embedding_batch_size
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            vectors = self._embedder.embed_texts([chunk.text for chunk in batch])
            if len(vectors) != len(batch):
                raise RuntimeError("Embedding provider returned mismatched vector count")

            embedded.extend(
                EmbeddedChunk(chunk=chunk, vector=vector)
                for chunk, vector in zip(batch, vectors, strict=True)
            )
        return embedded
