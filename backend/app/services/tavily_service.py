import logging
from typing import Dict, List, Optional

from tavily import TavilyClient
from tavily.errors import InvalidAPIKeyError

from app.core.config import settings

logger = logging.getLogger(__name__)


class TavilyService:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.client = None
        self.include_domains = [
            "indiacode.nic.in",
            "legislative.gov.in",
            "main.sci.gov.in",
            "sci.gov.in",
            "ecourts.gov.in",
            "doj.gov.in",
            "lawcommissionofindia.nic.in",
            "egazette.nic.in",
        ]

        if self.api_key:
            logger.info("Tavily live legal search configured.")
        else:
            logger.warning("TAVILY_API_KEY not found. Live legal search is disabled.")

    def _ensure_client(self):
        if not self.api_key:
            raise RuntimeError("TAVILY_API_KEY not found.")
        if self.client is None:
            self.client = TavilyClient(api_key=self.api_key)
        return self.client

    def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
    ) -> List[Dict]:
        if not self.api_key:
            return []

        try:
            response = self._ensure_client().search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False,
                include_raw_content=True,
                include_domains=include_domains or self.include_domains,
            )
            return [
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "text": result.get("raw_content") or result.get("content", ""),
                    "source": "tavily",
                    "score": result.get("score", 0.0),
                }
                for result in response.get("results", [])
            ]
        except InvalidAPIKeyError as exc:
            logger.warning("Tavily search skipped because the API key is invalid: %s", exc)
            return []
        except Exception:
            logger.exception("Tavily search failed.")
            return []


tavily_service = TavilyService()
