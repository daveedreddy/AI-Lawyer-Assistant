from app.services.nvidia_service import NvidiaService


def test_nvidia_service_builds_prompt_and_returns_text():
    service = NvidiaService()
    prompt = service._build_prompt(
        query="What is Article 21?",
        context="Article 21 protects life and personal liberty.",
    )
    response = service._build_fallback_answer(
        query="What is Article 21?",
        context="Article 21 protects life and personal liberty.",
    )
    assert "What is Article 21?" in prompt
    assert "Article 21 protects life and personal liberty." in prompt
    assert isinstance(response, str)
    assert response.strip()
