from typing import List, Dict

from sentence_transformers import CrossEncoder


class RerankerService:
    """
    Re-ranks retrieved evidence using a CrossEncoder.
    """

    def __init__(self):
        self.model = CrossEncoder(
            "BAAI/bge-reranker-base"
        )

    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:

        if not documents:
            return []

        pairs = [
            (query, doc["text"])
            for doc in documents
        ]

        scores = self.model.predict(pairs)

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        documents.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return documents[:top_k]


reranker_service = RerankerService()