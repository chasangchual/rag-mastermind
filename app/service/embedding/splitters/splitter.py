from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from dataclasses import dataclass, field
from typing import Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.model.document import Document


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
    def split(self, document: Document) -> list[Chunk]:
        raise NotImplementedError


class RecursiveTextSplitter(DocumentSplitter):
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split(self, document: Document) -> list[Chunk]:
        if document.text is None:
            return []

        pieces = self._splitter.split_text(document.text)
        return [
            Chunk(
                id=str(uuid4()),
                document_id=document.public_id,
                index=idx,
                text=chunk_text,
                metadata={
                    **(document.meta or {}),
                    "source": document.source,
                    "ext": document.extension,
                },
            )
            for idx, chunk_text in enumerate(pieces)
        ]
