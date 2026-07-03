from app.services.provider_manager import provider_manager, Provider
from app.services.nvidia_service import nvidia_service
from typing import Dict, Iterator, List, Optional


class LLMRouter:

    def generate(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:

        for provider in provider_manager.providers():
            try:
                if provider == Provider.NVIDIA:
                    return nvidia_service.generate_response(
                        query=query,
                        context=context,
                        conversation_history=conversation_history,
                    )

                if provider in {Provider.GEMINI, Provider.OPENROUTER, Provider.OPENAI, Provider.GROQ, Provider.LOCAL}:
                    continue

            except Exception as exc:
                raise RuntimeError(f"LLM provider '{provider.value}' failed: {exc}") from exc

        return nvidia_service.generate_response(
            query=query,
            context=context,
            conversation_history=conversation_history,
        )

    def stream_generate(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Iterator[str]:
        for provider in provider_manager.providers():
            if provider != Provider.NVIDIA:
                continue
            try:
                yield from nvidia_service.stream_response(
                    query=query,
                    context=context,
                    conversation_history=conversation_history,
                )
                return
            except Exception as exc:
                raise RuntimeError(f"LLM provider '{provider.value}' failed: {exc}") from exc

        yield from nvidia_service.stream_response(
            query=query,
            context=context,
            conversation_history=conversation_history,
        )


llm_router = LLMRouter()
