from abc import ABC

# Framework independent RAG retriver base class 
class Retriver(ABC):
    def __init__(self, config: dict | None = None) -> None:
        self.config = config

    def retrieve(self, query: str, limit: int = 5) -> list[str]:
        raise NotImplementedError("Subclasses must implement this method.")