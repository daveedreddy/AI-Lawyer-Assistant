import logging
from typing import Dict, List

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class RerankerService:
    def __init__(self):
        self.model = None

    def _ensure_model(self) -> None:
        if self.model is None:
            logger.info("Loading BAAI/bge-reranker-base reranker model.")
            self.model = CrossEncoder("BAAI/bge-reranker-base")

    def rerank(self, query: str, documents: List[Dict], top_k: int = 5) -> List[Dict]:
        if not documents:
            return []

        try:
            self._ensure_model()
            scores = self.model.predict([(query, doc["text"]) for doc in documents])
            for doc, score in zip(documents, scores):
                doc["rerank_score"] = float(score)
            return sorted(documents, key=lambda item: item["rerank_score"], reverse=True)[:top_k]
        except Exception as exc:
            logger.exception("Reranking failed, using retrieval scores: %s", exc)
            return sorted(
                documents,
                key=lambda item: float(item.get("score", 0.0) or 0.0),
                reverse=True,
            )[:top_k]


reranker_service = RerankerService()
