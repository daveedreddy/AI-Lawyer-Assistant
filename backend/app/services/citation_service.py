import re
from typing import Dict, List


class CitationService:
    def build_citations(self, documents: List[Dict]) -> List[Dict]:
        citations = []
        for index, document in enumerate(documents, start=1):
            metadata = document.get("metadata", {}) or {}
            title = metadata.get("title") or document.get("title") or f"Source {index}"
            url = metadata.get("url") or document.get("url") or ""
            source = metadata.get("source") or document.get("source") or "local"
            citations.append(
                {
                    "id": f"[{index}]",
                    "title": title,
                    "source": source,
                    "url": url,
                }
            )
        return citations

    def format_citations(self, citations: List[Dict]) -> str:
        if not citations:
            return "No sources cited."
        lines = ["Sources Used"]
        for citation in citations:
            lines.append(f"- {citation['id']} {citation['title']} ({citation['source']})")
            if citation.get("url"):
                lines.append(f"  URL: {citation['url']}")
        return "\n".join(lines)


citation_service = CitationService()
