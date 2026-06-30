from app.services.nvidia_service import NvidiaService


def test_nvidia_service_builds_prompt_and_returns_text():
    service = NvidiaService()
    response = service.generate_response(
        query="What is Article 21?",
        context="Article 21 protects life and personal liberty."
    )
    assert isinstance(response, str)
    assert response.strip()
