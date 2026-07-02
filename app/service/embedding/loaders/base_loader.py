
from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4
from typing import List, Any

@dataclass(slots=True)
class ContentSource:
    """Normalized document object used across the ingestion pipeline."""

    id: str
    source: str
    type: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class LoaderDependencyError(RuntimeError):
    pass


class ContentSourceLoader(ABC):
    @abstractmethod
    def supports(self, source: str | Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def load(self, source: str | Path) -> List[ContentSource]:
        raise NotImplementedError


class ContentSourceLoaderRegistry:
    def __init__(self, loaders: list[ContentSourceLoader] | None = None) -> None:
        self._loaders: list[ContentSourceLoader] = loaders or []

    def register(self, loader: ContentSourceLoader) -> None:
        self._loaders.append(loader)

    def get_loader(self, source: str | Path) -> ContentSourceLoader:
        for loader in self._loaders:
            if loader.supports(source):
                return loader
        raise ValueError(f"No loader found for source: {source}")

    def load(self, source: str | Path) -> List[ContentSource]:
        return self.get_loader(source).load(source)


def build_content_source(source: str | Path, doc_type: str, text: str, metadata: dict | None = None) -> ContentSource:
    return ContentSource(
        id=str(uuid4()),
        source=str(source),
        type=doc_type,
        text=text,
        metadata=metadata or {},
    )
