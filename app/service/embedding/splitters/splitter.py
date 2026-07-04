from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from dataclasses import dataclass, field
from typing import Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.model.document import Document
from app.service.embedding.loader.base_loader import ContentSource


@dataclass(slots=True)
class Chunk:
    """A chunk generated from a source document."""

    id: str
    document_id: UUID
    index: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EmbeddedChunk:
    """A chunk plus its embedding vector."""

    chunk: Chunk
    vector: list[float]


class DocumentSplitter(ABC):
    @abstractmethod
    def split(self, contentSource: ContentSource) -> list[Chunk]:
        raise NotImplementedError


class RecursiveTextSplitter(DocumentSplitter):
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split(self, contentSource: ContentSource) -> list[Chunk]:
        if contentSource.text is None:
            return []

        pieces = self._splitter.split_text(contentSource.text)
        return [
            Chunk(
                id=str(uuid4()),
                document_id=contentSource.public_id,
                index=idx,
                text=chunk_text,
                metadata={
                    **(contentSource.meta or {}),
                    "source": contentSource.source,
                    "ext": contentSource.extension,
                },
            )
            for idx, chunk_text in enumerate(pieces)
        ]
