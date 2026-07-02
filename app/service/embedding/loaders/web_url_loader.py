from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from langchain_community.document_loaders import WebBaseLoader
from app.service.embedding.loaders.base_loader import (
    ContentSourceLoader,
    build_content_source,
    ContentSource,
)


class WebUrlLoader(ContentSourceLoader):
    def supports(self, source: str | Path) -> bool:
        if isinstance(source, Path):
            return False
        parsed = urlparse(source)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def load(self, source: str | Path) -> list[ContentSource]:
        url = str(source)
        docs = WebBaseLoader(web_paths=[url]).load()
        return [
            build_content_source(
                url,
                "url",
                doc.page_content,
                {
                    "title": doc.metadata.get("title"),
                    "language": doc.metadata.get("language"),
                },
            )
            for doc in docs
            if doc.page_content
        ]
