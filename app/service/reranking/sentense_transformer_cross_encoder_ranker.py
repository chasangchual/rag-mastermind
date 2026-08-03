from __future__ import annotations

import logging
import os
from pathlib import Path

import torch
from huggingface_hub.errors import LocalEntryNotFoundError
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from sentence_transformers.base.modules import Transformer

from app.service.reranking.base_reranker import Reranker

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"

CACHE_DIR = Path(
    os.getenv(
        "HF_MODEL_CACHE",
        "./data/huggingface",
    )
).resolve()

CACHE_DIR.mkdir(parents=True, exist_ok=True)


class SentenceTransformerCrossEncoderRanker(Reranker):
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        batch_size: int = 5,
        max_length: int = 512,
        normalize_scores: bool = False,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        if max_length <= 0:
            raise ValueError("max_length must be greater than zero")

        self._model_name = model_name
        self._batch_size = batch_size
        self._max_length = max_length
        self._normalize_scores = normalize_scores

        self._model = self.load_cross_encoder(
            model_name=model_name,
            max_length=max_length,
            normalize_scores=normalize_scores,
        )

    def load_cross_encoder(
        self,
        model_name: str = DEFAULT_MODEL,
        max_length: int = 512,
        normalize_scores: bool = False,
    ) -> CrossEncoder:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        activation_fn = torch.nn.Sigmoid() if normalize_scores else None

        def create_model(
            local_files_only: bool,
        ) -> CrossEncoder:
            shared_kwargs = {
                "cache_dir": str(CACHE_DIR),
                "local_files_only": local_files_only,
            }

            transformer_module = Transformer(
                model_name_or_path=model_name,
                transformer_task="sequence-classification",
                model_kwargs=shared_kwargs.copy(),
                processor_kwargs={
                    **shared_kwargs,
                    "model_max_length": max_length,
                },
                config_kwargs=shared_kwargs.copy(),
            )

            return CrossEncoder(
                modules=[transformer_module],
                activation_fn=activation_fn,
            )

        try:
            logger.info(
                "Attempting to load reranker '%s' from local cache: %s",
                model_name,
                CACHE_DIR,
            )

            model = create_model(
                local_files_only=True,
            )

            logger.info(
                "Reranker '%s' loaded from local cache",
                model_name,
            )

            return model

        except (LocalEntryNotFoundError, OSError) as exc:
            logger.info(
                "Reranker '%s' was not found or was incomplete locally. "
                "Downloading from Hugging Face. Reason: %s",
                model_name,
                exc,
            )

            model = create_model(
                local_files_only=False,
            )

            logger.info(
                "Reranker '%s' downloaded and cached at: %s",
                model_name,
                CACHE_DIR,
            )

            return model

    def rerank(
        self,
        query: str,
        candidates: list[Document],
    ) -> list[tuple[Document, float]]:
        """
        Rank candidates according to their relevance to the query.

        Args:
            query: Query used to rank the candidate documents.
            candidates: Candidate text values to rank.

        Returns:
            Candidate and score tuples sorted by descending score.
        """
        query = query.strip()

        if not query:
            raise ValueError("query must not be empty")

        if not candidates:
            return []

        inputs = [(query, candidate.page_content) for candidate in candidates]

        scores = self._model.predict(
            inputs,
            batch_size=self._batch_size,
            show_progress_bar=False,
        )

        ranked_candidates = [
            (candidate, float(score))
            for candidate, score in zip(
                candidates,
                scores,
                strict=True,
            )
        ]

        ranked_candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return ranked_candidates
