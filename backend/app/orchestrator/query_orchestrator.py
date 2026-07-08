import logging
import hashlib
from typing import Dict, Iterator, List, Optional

from app.models.response_models import QueryResponse, RetrievedDocument
from app.services.cache_service import cache_service
from app.services.citation_service import citation_service
from app.services.confidence_service import confidence_service
from app.services.evidence_fusion_service import evidence_fusion_service
from app.services.legal_source_router import legal_source_router
from app.services.llm_router import llm_router
from app.utils.logging_utils import log_operation

logger = logging.getLogger(__name__)


class QueryOrchestrator:
    @staticmethod
    def _build_contextual_query(
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        if not conversation_history:
            return query

        history_parts = []
        for item in conversation_history[-6:]:
            role = item.get("role", "")
            content = " ".join((item.get("content") or "").split())
            if not content:
                continue
            if len(content) > 500:
                content = content[:497].rstrip() + "..."
            history_parts.append(f"{role}: {content}")

        if not history_parts:
            return query

        return "\n".join(history_parts + [f"current question: {query}"])

    @staticmethod
    def _cache_key(
        query: str,
        top_k: int,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        if not conversation_history:
            return f"query:{query.lower()}:{top_k}"

        history_text = "|".join(
            f"{item.get('role', '')}:{' '.join((item.get('content') or '').split())}"
            for item in conversation_history[-8:]
        )
        history_hash = hashlib.sha256(history_text.encode("utf-8")).hexdigest()[:16]
        return f"query:{query.lower()}:{top_k}:history:{history_hash}"

    def _prepare_documents(self, query: str, documents: List[Dict], top_k: int) -> List[Dict]:
        if not documents:
            return []

        if len(documents) <= 2 or top_k <= 2:
            return sorted(
                documents,
                key=lambda item: float(item.get("score", 0.0) or 0.0),
                reverse=True,
            )[:top_k]

        from app.services.reranker_service import reranker_service

        ranked = reranker_service.rerank(query=query, documents=documents, top_k=top_k)
        return ranked[:top_k]

    @staticmethod
    def _should_use_web_search(query: str, local_results: List[Dict]) -> bool:
        if not local_results:
            return True

        query_lower = query.lower()
        strong_local_match = any(item.get("score", 0.0) >= 0.8 for item in local_results)
        if strong_local_match:
            return False

        if any(
            term in query_lower
            for term in (
                "latest",
                "recent",
                "amendment",
                "new",
                "today",
                "2024",
                "2025",
                "case law",
                "judgment",
                "update",
            )
        ):
            return True

        return len(local_results) < 2

    def prepare_evidence(
        self,
        query: str,
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        from app.services.retrieval_service import retrieval_service

        retrieval_query = self._build_contextual_query(query, conversation_history)
        local_results = self._prepare_documents(
            retrieval_query,
            retrieval_service.search(query=retrieval_query, top_k=top_k),
            top_k,
        )
        use_web_search = self._should_use_web_search(retrieval_query, local_results)
        web_results = []
        if use_web_search:
            web_results = self._prepare_documents(
                retrieval_query,
                legal_source_router.search(retrieval_query),
                top_k,
            )
        documents = local_results + web_results
        context = evidence_fusion_service.build_context(
            local_results=local_results,
            web_results=web_results,
        )
        citations = citation_service.build_citations(documents)
        retrieved_documents = [
            RetrievedDocument(
                text=item["text"],
                metadata=item.get("metadata", {}),
                score=item.get("score", 0.0),
            )
            for item in documents
        ]

        return {
            "context": context,
            "citations": citations,
            "documents": documents,
            "retrieved_documents": retrieved_documents,
        }

    def process_query(
        self,
        query: str,
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> QueryResponse:
        clean_query = query.strip()
        cache_key = self._cache_key(clean_query, top_k, conversation_history)
        cached = cache_service.get(cache_key)
        if cached is not None:
            return cached

        with log_operation("process_query"):
            evidence = self.prepare_evidence(
                clean_query,
                top_k,
                conversation_history=conversation_history,
            )
            answer = llm_router.generate(
                query=clean_query,
                context=evidence["context"],
                conversation_history=conversation_history,
            )
            confidence = confidence_service.score(
                query=clean_query,
                documents=evidence["documents"],
                answer=answer,
            )

            response = QueryResponse(
                query=clean_query,
                answer=answer,
                retrieved_documents=evidence["retrieved_documents"],
                confidence=confidence,
                citations=evidence["citations"],
                sources=[c["url"] for c in evidence["citations"] if c.get("url")],
                context=evidence["context"],
            )

            cache_service.set(cache_key, response)
            return response

    def stream_answer(
        self,
        query: str,
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Iterator[Dict]:
        clean_query = query.strip()
        evidence = self.prepare_evidence(
            clean_query,
            top_k,
            conversation_history=conversation_history,
        )
        answer_parts: List[str] = []

        yield {
            "type": "metadata",
            "citations": evidence["citations"],
            "sources": [c["url"] for c in evidence["citations"] if c.get("url")],
            "retrieved_documents": [doc.model_dump() for doc in evidence["retrieved_documents"]],
            "context": evidence["context"],
        }

        for chunk in llm_router.stream_generate(
            query=clean_query,
            context=evidence["context"],
            conversation_history=conversation_history,
        ):
            answer_parts.append(chunk)
            yield {"type": "delta", "content": chunk}

        answer = "".join(answer_parts).strip()
        confidence = confidence_service.score(
            query=clean_query,
            documents=evidence["documents"],
            answer=answer,
        )
        yield {
            "type": "done",
            "answer": answer,
            "confidence": confidence,
            "citations": evidence["citations"],
            "sources": [c["url"] for c in evidence["citations"] if c.get("url")],
            "retrieved_documents": [doc.model_dump() for doc in evidence["retrieved_documents"]],
            "context": evidence["context"],
        }


query_orchestrator = QueryOrchestrator()
