from __future__ import annotations

from dataclasses import dataclass, field

from typing import List
from uuid import UUID
from sqlalchemy.orm import registry

from app.service.embedding import build_default_registry
from app.service.embedding.embedders.lms_qwen_8b_embedder import LMStudioEmbeddingProvider
from app.service.embedding.loaders.base_loader import ContentSource, ContentSourceLoaderRegistry
from app.service.embedding.splitters.splitter import (
    DocumentSplitter,
    RecursiveTextSplitter,
    EmbeddedChunk,
    Chunk,
)
from app.service.embedding.embedders.base_embedder import (
    EmbeddingProvider,
    HashEmbeddingProvider,
)


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

    def process_document(self, public_id: UUID, file_path: str) ->  list[EmbeddedChunk]:
        content_sources: List[ContentSource] = self._registry.load(file_path)

        chunks: list[Chunk] = []
        for content_source in content_sources:
            chunks.extend(self._splitter.split(public_id, content_source))

        return self._embed_chunks(chunks)
        
    def _embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        if not chunks:
            return []

        embedded: list[EmbeddedChunk] = []
        batch_size = self._config.embedding_batch_size
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            vectors = self._embedder.embed_texts([chunk.text for chunk in batch])
            if len(vectors) != len(batch):
                raise RuntimeError(
                    "Embedding provider returned mismatched vector count"
                )

            embedded.extend(
                EmbeddedChunk(chunk=chunk, vector=vector)
                for chunk, vector in zip(batch, vectors, strict=True)
            )
        return embedded


def build_default_pipeline(
    config: PipelineConfig | None = None,
    embedder: EmbeddingProvider | None = None,
) -> EmbeddingPipeline:
    cfg = config or PipelineConfig()
    return EmbeddingPipeline(
        registry=build_default_registry(text_encoding=cfg.text_encoding),
        splitter=RecursiveTextSplitter(
            chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap
        ),
        embedder=embedder or HashEmbeddingProvider(),
        config=cfg,
    )


default_pipeline = build_default_pipeline(embedder=LMStudioEmbeddingProvider())