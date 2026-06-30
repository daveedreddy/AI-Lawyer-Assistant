import os
import logging
from typing import List, Dict

from dotenv import load_dotenv
from tavily import TavilyClient
from tavily.errors import InvalidAPIKeyError

load_dotenv()

logger = logging.getLogger(__name__)


class TavilyService:
    """
    Live Legal Search using Tavily.

    Returns normalized evidence for the Evidence Fusion layer.
    """

    def __init__(self):

        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = None

        self.include_domains = [
            "indiacode.nic.in",
            "legislative.gov.in",
            "main.sci.gov.in",
            "sci.gov.in",
            "ecourts.gov.in",
            "doj.gov.in",
            "lawcommissionofindia.nic.in",
            "egazette.nic.in"
        ]

        if self.api_key:
            logger.info("Tavily Service initialized.")
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
    include_domains: List[str] | None = None
) -> List[Dict]:

        if not self.api_key:
            return []

        try:
            client = self._ensure_client()

            response = client.search(

                query=query,

                search_depth="advanced",

                max_results=max_results,

                include_answer=False,

                include_raw_content=True,

                include_domains=include_domains or self.include_domains
            )

            evidence = []

            for result in response.get("results", []):

                evidence.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "text": result.get("raw_content", result.get("content", "")),
                    "source": "tavily",
                    "score": result.get("score", 0.0)

                })

            return evidence

        except InvalidAPIKeyError as exc:
            logger.warning("Tavily search skipped because the API key is invalid: %s", exc)
            return []
        except Exception as e:
            logger.exception("Tavily search failed.")
            return []


tavily_service = TavilyService()