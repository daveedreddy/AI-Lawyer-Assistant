from app.orchestrator.query_orchestrator import QueryOrchestrator


def test_skips_web_search_when_local_results_are_strong():
    orchestrator = QueryOrchestrator()
    local_results = [
        {"text": "Article 21 protects personal liberty", "score": 0.95},
        {"text": "Procedure established by law", "score": 0.92},
    ]

    assert not orchestrator._should_use_web_search(
        "What is Article 21 of the Constitution?",
        local_results,
    )


def test_uses_web_search_for_recent_or_specific_updates():
    orchestrator = QueryOrchestrator()
    local_results = [{"text": "Older summary", "score": 0.65}]

    assert orchestrator._should_use_web_search(
        "What is the latest amendment to the BNS?",
        local_results,
    )
