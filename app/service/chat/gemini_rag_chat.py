import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.app_config import get_config
from langchain_core.prompts.chat import ChatPromptTemplate
from app.repository.qdrant_repository import QdrantRepository
from app.service.chat.base_chat import MAX_HISTORY_TURNS, ChatProvider
from app.service.chat.gemini_chat import GEMINI_CHAT_MODEL
from app.service.embedding.embedders.lms_qwen_8b_embedder import LMStudioEmbeddingProvider
from app.service.retrieval.qdrant_retriver import QdrantRetriever
from app.service.reranking.sentense_transformer_cross_encoder_ranker import SentenceTransformerCrossEncoderRanker
from langchain_core.output_parsers import StrOutputParser

RERANK_SCORE_THRESHOLD = 0.0

class GeminiRagChatProvider(ChatProvider):
    def __init__(self, max_history_turns: int = MAX_HISTORY_TURNS, rerank_threshold: float = RERANK_SCORE_THRESHOLD) -> None:
        super().__init__(max_history_turns)
        config = get_config()
        self._retriever = QdrantRetriever(embedder=LMStudioEmbeddingProvider(), repository=QdrantRepository())
        self._reranker = SentenceTransformerCrossEncoderRanker(normalize_scores = True)  # Placeholder for the reranker component
        self._rerank_threshold = rerank_threshold
        self._model = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL, api_key=config.gemini_api_key, temperature=0.0)

    def set_retriever(self, retriever):
        self._retriever = retriever

    def set_reranker(self, reranker):
        self._reranker = reranker
    def get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template(
       '''You are a helpful assistant. 
       
Answer the question using only the context below. 
If the question cannot be answered from the context, say, "I don't know."

Context:
{context}

Question:
{question}
'''
         )

    def ask(self, question: str) -> str:
        if not self._retriever or not self._reranker :
            raise ValueError("Retriever, Reranker, and LLM service must be set before asking questions.")
        try:
            retrieved_docs = self._retriever.invoke(question)
            reranked_docs = self._reranker.rerank(question, retrieved_docs)
            top_docs = [doc for doc, score in reranked_docs if score >= self._rerank_threshold]

            if not top_docs:
                return "No relevant information found."

            chain = self.get_prompt_template() | self._model | StrOutputParser()
            return chain.invoke({'context': top_docs, 'question': question})
        except Exception as e:
            logging.error(f"Error during RAG process: {e}")
            return "An error occurred while processing your request. Please try again later."