import logging

from app.services.nvidia_service import nvidia_service

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Compatibility wrapper for the active NVIDIA backend.
    """

    def __init__(self):
        self.model_name = "nvidia/nemotron-3-ultra-550b-a55b"
        logger.info("Gemini compatibility wrapper using NVIDIA backend.")

    def generate_response(self, query: str, context: str) -> str:
        return nvidia_service.generate_response(query=query, context=context)


gemini_service = GeminiService()