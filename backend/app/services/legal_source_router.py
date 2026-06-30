from typing import List, Dict

from app.services.query_classifier import (
    query_classifier,
    QueryType,
)

from app.services.tavily_service import tavily_service


class LegalSourceRouter:
    """
    Routes live legal searches based on query intent.
    """

    def search(
        self,
        query: str
    ) -> List[Dict]:

        query_type = query_classifier.classify(query)

        if query_type == QueryType.CONSTITUTION:
            return tavily_service.search(
                query=query,
                max_results=5,
                include_domains=[
                    "indiacode.nic.in",
                    "legislative.gov.in"
                ]
            )

        elif query_type == QueryType.ACT:
            return tavily_service.search(
                query=query,
                max_results=5,
                include_domains=[
                    "indiacode.nic.in"
                ]
            )

        elif query_type == QueryType.CASE:
            return tavily_service.search(
                query=query,
                max_results=5,
                include_domains=[
                    "api.sci.gov.in",
                    "sci.gov.in",
                    "main.sci.gov.in"
                ]
            )

        return tavily_service.search(
            query=query,
            max_results=5
        )


legal_source_router = LegalSourceRouter()