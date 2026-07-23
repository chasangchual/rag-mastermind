from __future__ import annotations


from app.model.lms import lms_default_client 

from app.service.embedding.embedders.base_embedder import EmbeddingProvider

QWEN_EMBEDDING_06B_MODEL = "text-embedding-qwen3-embedding-0.6b"
QWEN_EMBEDDING_8B_MODEL = "text-embedding-qwen3-embedding-8b"
GEMMA_EMBEDDING_MODEL = "text-embedding-embeddinggemma-300m"

class LMStudioEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str | None) -> None:
        embedding_model = QWEN_EMBEDDING_8B_MODEL
        if 'qwen' in model.lower():
            embedding_model = QWEN_EMBEDDING_8B_MODEL
        elif 'gemma' in model.lower():
            embedding_model = GEMMA_EMBEDDING_MODEL
             
        self._embedder = lms_default_client.embedding.model(embedding_model)
         

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = [] 
        
        for text in texts:
            embedding = self._embedder.embed(text)
            embeddings.append(embedding)
            
        return embeddings
