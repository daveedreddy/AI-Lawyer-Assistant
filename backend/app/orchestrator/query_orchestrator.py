import logging
from typing import List, Dict

from app.models.response_models import QueryResponse, RetrievedDocument
from app.services.cache_service import cache_service
from app.services.citation_service import citation_service
from app.services.confidence_service import confidence_service
from app.services.evidence_fusion_service import evidence_fusion_service
from app.services.legal_source_router import legal_source_router
from app.services.llm_router import llm_router
from app.services.retrieval_service import retrieval_service
from app.services.reranker_service import reranker_service
from app.utils.logging_utils import log_operation

logger = logging.getLogger(__name__)


class QueryOrchestrator:
    """
    Central coordinator for the AI Lawyer backend.
    """

    def _prepare_documents(self, query: str, documents: List[Dict], top_k: int) -> List[Dict]:
        if not documents:
            return []
        ranked = reranker_service.rerank(query=query, documents=documents, top_k=top_k)
        return ranked[:top_k]

    def process_query(self, query: str, top_k: int = 5) -> QueryResponse:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        cache_key = f"query:{query.strip().lower()}:{top_k}"
        cached = cache_service.get(cache_key)
        if cached is not None:
            return cached

        with log_operation("process_query"):
            local_results = self._prepare_documents(query, retrieval_service.search(query=query, top_k=top_k), top_k)
            web_results = self._prepare_documents(query, legal_source_router.search(query), top_k)
            context = evidence_fusion_service.build_context(local_results=local_results, web_results=web_results)
            answer = llm_router.generate(query=query, context=context)
            citations = citation_service.build_citations(local_results + web_results)
            confidence = confidence_service.score(query=query, documents=local_results + web_results, answer=answer)

            retrieved_documents = [
                RetrievedDocument(
                    text=item["text"],
                    metadata=item.get("metadata", {}),
                    score=item.get("score", 0.0),
                )
                for item in local_results + web_results
            ]

            response = QueryResponse(
                query=query,
                answer=answer,
                retrieved_documents=retrieved_documents,
            )
            response.confidence = confidence
            response.citations = citations
            response.context = context

            cache_service.set(cache_key, response)
            return response


query_orchestrator = QueryOrchestrator()