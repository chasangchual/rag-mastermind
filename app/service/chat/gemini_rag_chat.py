import logging
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.prompt_values import PromptValue
from app.repository.qdrant_repository import QdrantRepository
from app.service.chat.gemini_chat import MAX_HISTORY_TURNS, GeminiChatProvider
from app.service.embedding.embedders.lms_qwen_8b_embedder import LMStudioEmbeddingProvider 
from app.service.retrieval.qdrant_retriver import QdrantRetriever
from app.service.reranking.sentense_transformer_cross_encoder_ranker import SentenceTransformerCrossEncoderRanker
from langchain_core.output_parsers import StrOutputParser

class GeminiRagChatProvider(GeminiChatProvider):
    def __init__(self, max_history_turns: int = MAX_HISTORY_TURNS) -> None:
        super().__init__(max_history_turns)
        self._retriever = QdrantRetriever(embedder=LMStudioEmbeddingProvider(), repository=QdrantRepository())
        self._reranker = SentenceTransformerCrossEncoderRanker()  # Placeholder for the reranker component

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

    def get_prompt(self, question: str, docs: list) -> PromptValue:
        prompt : ChatPromptTemplate = self.get_prompt_template()      
        return prompt.invoke({'context': docs, 'question': question})
        
    def ask(self, question: str) -> str:
        if not self._retriever or not self._reranker :
            raise ValueError("Retriever, Reranker, and LLM service must be set before asking questions.")
        try:
            # Retrieve relevant documents based on the question
            retrieved_docs = self._retriever.invoke(question)
            
            prompt_template = self.get_prompt_template()
            prompt = self.get_prompt(question, retrieved_docs)
            
            # response = super().ask(prompt)  # Call the parent class's ask method to maintain history 
            
            chain = prompt_template | self._model | StrOutputParser()
            
            # Rerank the retrieved documents
            # response = reranked_docs = self._reranker.rerank(retrieved_docs, question)

            # Generate a response using the LLM service with the top-ranked document
            # top_doc = reranked_docs[0] if reranked_docs else None
            
            top_doc = retrieved_docs
            
            if top_doc:
                response = chain.invoke({'context': retrieved_docs, 'question': question})
                # response = self._llm_service.generate_response(question, top_doc)
                return response
            else:
                return "No relevant information found."
        except Exception as e:
            logging.error(f"Error during RAG process: {e}")
            return "An error occurred while processing your request. Please try again later."