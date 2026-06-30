from typing import Dict, List


class ConfidenceService:
    def score(self, query: str, documents: List[Dict], answer: str) -> float:
        if not documents:
            return 0.3
        score = min(0.95, 0.4 + (len(documents) * 0.08) + (0.1 if answer.strip() else 0.0))
        query_terms = set(query.lower().split())
        matched_terms = [term for term in query_terms if term and term.isalpha() and term in answer.lower()]
        score += min(0.15, len(matched_terms) * 0.02)
        return round(max(0.1, min(0.99, score)), 2)


confidence_service = ConfidenceService()
