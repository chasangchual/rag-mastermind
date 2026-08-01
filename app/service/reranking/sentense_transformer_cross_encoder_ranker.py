from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import logger
import torch
from sentence_transformers import CrossEncoder
from huggingface_hub.errors import LocalEntryNotFoundError

from app.service.reranking.base_reranker import Reranker

# logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # You can change this to any other cross-encoder model available in the sentence-transformers library
CACHE_DIR = Path(
    os.getenv(
        "HF_MODEL_CACHE",
        "./data/huggingface",
    )
)

class SentenceTransformerCrossEncoderRanker(Reranker):
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        batch_size: int = 5,
        max_length: int = 512,
        normalize_scores: bool = False,
    ):
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        if max_length <= 0:
            raise ValueError("max_length must be greater than zero")
        
        self._model_name = model_name
        self._batch_size = batch_size
        self._max_length = max_length
        self._normalize_scores = normalize_scores
        
        self._model = self.load_cross_encoder(model_name, max_length, normalize_scores)   # Use GPU if available

    def load_cross_encoder(self, model_name : str = DEFAULT_MODEL, max_length: int = 512, normalize_scores: bool = False) -> CrossEncoder:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Some reranker models return raw logits.
        # Sigmoid converts a single score to approximately 0–1 while preserving the ranking order.
        activation_fn = torch.nn.Sigmoid() if normalize_scores else None

        try:
            logger.info("Attempting to load reranker from local cache")

            return CrossEncoder(
                model_name_or_path=model_name,
                max_length=max_length,
                activation_fn=activation_fn,
                cache_folder=str(CACHE_DIR),
                local_files_only=True,
            )

        except (LocalEntryNotFoundError, OSError) as exc:
            logger.info(
                "Reranker was not found in the local cache. "
                "Downloading it from Hugging Face. Reason: %s",
                exc,
            )

            return CrossEncoder(
                model_name_or_path=model_name,
                max_length=max_length,
                activation_fn=activation_fn,
                cache_folder=str(CACHE_DIR),
                local_files_only=False,
            )

    def rerank(self, query: str, candidates: list[str]) -> list[str]:
        """
        Rank the candidates based on their relevance to the query using a cross-encoder model.

        :param query: The input query string.
        :param candidates: A list of candidate strings to be ranked.
        :return: A list of tuples containing candidates and their corresponding scores, sorted by score in descending order.
        """
        # Prepare the input for the cross-encoder
        inputs = [(query, candidate) for candidate in candidates]

        # Get the scores from the model
        scores = self._model.predict(inputs)

        # Combine candidates with their scores
        ranked_candidates = list(zip(candidates, scores))

        # Sort candidates by score in descending order
        ranked_candidates.sort(key=lambda x: x[1], reverse=True)

        return ranked_candidates
