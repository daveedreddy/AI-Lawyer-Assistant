from typing import Any, Dict, List


class EvidenceFusionService:
    """
    Combines evidence from multiple sources into a structured context for the LLM.
    """

    def _normalize(self, document: Dict[str, Any]) -> Dict[str, Any]:
        metadata = document.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}
        text = (document.get("text") or "").strip()
        return {
            "text": text,
            "metadata": metadata,
            "score": float(document.get("score", 0.0) or 0.0),
            "source": metadata.get("source") or document.get("source") or "unknown",
            "title": metadata.get("title") or document.get("title") or "",
            "url": metadata.get("url") or "",
        }

    def _deduplicate(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped = []
        seen = set()
        for document in documents:
            normalized = self._normalize(document)
            key = (normalized["source"], normalized["title"], normalized["url"], normalized["text"][:180])
            if key in seen:
                continue
            seen.add(key)
            deduped.append(normalized)
        return deduped

    def _prioritize(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        priority_order = {
            "constitution": 0,
            "bare_act": 1,
            "supremecourt": 2,
            "highcourt": 3,
            "official": 4,
            "tavily": 5,
            "unknown": 6,
        }
        return sorted(
            documents,
            key=lambda item: (
                priority_order.get(str(item["source"]).lower(), 99),
                -float(item["score"]),
            ),
        )

    def build_context(self, local_results: List[Dict], web_results: List[Dict]) -> str:
        merged = []
        for document in self._prioritize(self._deduplicate([*local_results, *web_results])):
            merged.append(
                f"""
Source: {document['source']}
Title: {document['title']}
URL: {document['url']}
Score: {document['score']}
Content: {document['text']}
------------------------------------------------------------
"""
            )

        if not merged:
            return "No relevant legal evidence was found."

        return "\n".join(merged)


evidence_fusion_service = EvidenceFusionService()