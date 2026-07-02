from uvicorn.config import is_dir

from app.service.embedding.loaders.base_loader import (
    ContentSourceLoader,
    build_content_source,
    ContentSource
)
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
)

import logging
from typing import List


class DocumentLoader(ContentSourceLoader):
    extensions: set[str] = set()

    def supports(self, source: str | Path) -> bool:
        source_path = Path(source)
        return source_path.suffix.lower() in self.extensions


class TextFileLoader(DocumentLoader):
    extensions = {".txt", ".md", ".rst"}

    def __init__(self, encoding: str = "utf-8") -> None:
        self._encoding = encoding

    def load(self, source: str | Path) -> List[ContentSource]:
        path = Path(source)
        text = path.read_text(encoding=self._encoding)
        return [
            build_content_source(path, "text", text, {"extension": path.suffix.lower()})
        ]


class PdfLoader(DocumentLoader):
    extensions = {".pdf"}

    def load(self, source: str | Path) -> List[ContentSource]:
        try:
            path = Path(source)
            suffix = path.suffix
            if suffix in self.extensions:
                pages = PyPDFLoader(file_path=str(path)).load()
            else:
                raise ValueError(f"unsupported extension {suffix}")
        except Exception as ex:
            logging.warning(f"Failed to load PDF document {source}: {ex}")
            raise ex

        return [
            build_content_source(
                path,
                "pdf",
                page.page_content,
                {
                    "extension": path.suffix,
                    "page": page.metadata.get("page"),
                    "source": page.metadata.get("source", str(path)),
                },
            )
            for page in pages
            if page.page_content
        ]


class WordLoader(DocumentLoader):
    extensions = {".doc", ".docx"}

    def load(self, source: str | Path) -> List[ContentSource]:
        try:
            path = Path(source)
            suffix = path.suffix
            if suffix in self.extensions:
                loader = UnstructuredWordDocumentLoader(
                    file_path=str(path), mode="elements"
                )
                pages = loader.load()
            else:
                raise ValueError(f"unsupported extension {suffix}")
        except Exception as ex:
            logging.warning(f"Failed to load Word document {source}: {ex}")
            raise ex

        return [
            build_content_source(
                path,
                "doc",
                page.page_content,
                {
                    "extension": path.suffix,
                    "page": page.metadata.get("page"),
                    "source": page.metadata.get("source", str(path)),
                },
            )
            for page in pages
            if page.page_content
        ]


class PowerpointLoader(DocumentLoader):
    extensions = {".ppt", ".pptx"}

    def load(self, source: str | Path) -> List[ContentSource]:
        try:
            path = Path(source)
            suffix = path.suffix
            if suffix in self.extensions:
                loader = UnstructuredPowerPointLoader(
                    file_path=str(path), mode="elements"
                )
                pages = loader.load()
            else:
                raise ValueError(f"unsupported extension {suffix}")
        except Exception as ex:
            logging.warning(f"Failed to load Powerpoint document {source}: {ex}")
            raise ex

        return [
            build_content_source(
                path,
                "ppt",
                page.page_content,
                {
                    "extension": path.suffix,
                    "page": page.metadata.get("page"),
                    "source": page.metadata.get("source", str(path)),
                },
            )
            for page in pages
            if page.page_content
        ]


class ExcelLoader(DocumentLoader):
    extensions = {".xls", ".xlsx"}

    def load(self, source: str | Path) -> List[ContentSource]:
        try:
            path = Path(source)
            suffix = path.suffix
            if suffix in self.extensions:
                loader = UnstructuredExcelLoader(file_path=str(path), mode="elements")
                pages = loader.load()
            else:
                raise ValueError(f"unsupported extension {suffix}")
        except Exception as ex:
            logging.warning(f"Failed to load Excel document {source}: {ex}")
            raise ex

        return [
            build_content_source(
                path,
                "ppt",
                page.page_content,
                {
                    "extension": path.suffix,
                    "page": page.metadata.get("page"),
                    "source": page.metadata.get("source", str(path)),
                },
            )
            for page in pages
            if page.page_content
        ]


class MarkdownLoader(DocumentLoader):
    extensions = {".md"}

    def load(self, source: str | Path) -> List[ContentSource]:
        try:
            path = Path(source)
            suffix = path.suffix
            if suffix in self.extensions:
                loader = UnstructuredMarkdownLoader(
                    file_path=str(path), mode="elements"
                )
                pages = loader.load()
            else:
                raise ValueError(f"unsupported extension {suffix}")
        except Exception as ex:
            logging.warning(f"Failed to load markdown document {source}: {ex}")
            raise ex

        return [
            build_content_source(
                path,
                "ppt",
                page.page_content,
                {
                    "extension": path.suffix,
                    "page": page.metadata.get("page"),
                    "source": page.metadata.get("source", str(path)),
                },
            )
            for page in pages
            if page.page_content
        ]
