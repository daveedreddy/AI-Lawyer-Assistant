from app.services.provider_manager import provider_manager, Provider
from app.services.nvidia_service import nvidia_service


class LLMRouter:

    def generate(
        self,
        query: str,
        context: str
    ) -> str:

        for provider in provider_manager.providers():
            try:
                if provider == Provider.NVIDIA:
                    return nvidia_service.generate_response(
                        query=query,
                        context=context
                    )

                if provider in {Provider.GEMINI, Provider.OPENROUTER, Provider.OPENAI, Provider.GROQ, Provider.LOCAL}:
                    continue

            except Exception as exc:
                raise RuntimeError(f"LLM provider '{provider.value}' failed: {exc}") from exc

        return nvidia_service.generate_response(
            query=query,
            context=context
        )


llm_router = LLMRouter()