from enum import Enum


class QueryType(str, Enum):
    CONSTITUTION = "constitution"
    ACT = "act"
    CASE = "case"
    BARE_ACT = "bare_act"
    GENERAL = "general"


class QueryClassifier:

    def classify(self, query: str) -> QueryType:

        q = query.lower()

        if "article" in q or "constitution" in q:
            return QueryType.CONSTITUTION

        if "section" in q:
            return QueryType.ACT

        if (
            "vs" in q
            or " v. " in q
            or "judgment" in q
            or "case" in q
            or "petition" in q
        ):
            return QueryType.CASE

        return QueryType.GENERAL


query_classifier = QueryClassifier()