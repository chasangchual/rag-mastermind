from app.service.embedding.loaders.base_loader import ContentSourceLoaderRegistry
from app.service.embedding.loaders.file_loader import TextFileLoader, PdfLoader, WordLoader, PowerpointLoader, ExcelLoader, MarkdownLoader
from app.service.embedding.loaders.web_url_loader import WebUrlLoader

def build_default_registry(text_encoding: str = "utf-8") -> ContentSourceLoaderRegistry:
    registry = ContentSourceLoaderRegistry()
    registry.register(WebUrlLoader())
    registry.register(TextFileLoader(encoding=text_encoding))
    registry.register(PdfLoader())
    registry.register(WordLoader())
    registry.register(ExcelLoader())
    registry.register(PowerpointLoader())
    registry.register(MarkdownLoader())
    return registry
