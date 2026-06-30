from app.services.nvidia_service import NvidiaService


def test_article_21_fallback_answer_is_conversational():
    service = NvidiaService()
    answer = service._build_fallback_answer("What is Article 21?", "")
    assert "Article 21" in answer
    assert "personal liberty" in answer.lower()
