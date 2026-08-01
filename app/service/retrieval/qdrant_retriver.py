import logging

from app.repository.qdrant_repository import QdrantRepository
from app.service.embedding.embedders.base_embedder import EmbeddingProvider

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

class QdrantRetriever(BaseRetriever):
    embedder: EmbeddingProvider
    repository: QdrantRepository
    limit: int = 5

    model_config = {"arbitrary_types_allowed": True}

    def retrieve(self, query: str, limit: int | None = None) -> list[dict]:
        query_vector = self._embedder.embed_texts([query])[0]
        if not query_vector:
            logging.error(f"Failed to embed query text: '{query}'")
            return []

        try:
            results = self._repository.search(query_vector, limit=limit or self._limit)
        except Exception as e:
            logging.error(
                f"Error during retrieval from Qdrant for the query '{query}'. Error: {e}"
            )
            return []

        return [
            {"id": result.id, "payload": result.payload, "score": result.score}
            for result in results
            if result.payload
        ]

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        query_vector = self.embedder.embed_texts([query])[0]
        if not query_vector:
            logging.error(f"Failed to embed query text: '{query}'")
            return []

        try:
            results = self.repository.search(query_vector, limit=self.limit)
        except Exception as e:
            logging.error(
                f"Error during retrieval from Qdrant for the query '{query}'. Error: {e}"
            )
            return []

        documents = []
        for result in results:
            if not result.payload or "text" not in result.payload:
                continue
            metadata = {k: v for k, v in result.payload.items() if k != "text"}
            metadata["id"] = result.id
            metadata["score"] = result.score
            documents.append(
                Document(page_content=result.payload["text"], metadata=metadata)
            )

        return documents
