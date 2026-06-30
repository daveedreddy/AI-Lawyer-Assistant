import logging

from app.services.nvidia_service import nvidia_service

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Compatibility wrapper for the active NVIDIA backend.
    """

    def __init__(self):
        self.model = "nvidia/nemotron-3-ultra-550b-a55b"
        logger.info("OpenAI compatibility wrapper using NVIDIA backend.")

    def generate_response(self, query: str, context: str) -> str:
        return nvidia_service.generate_response(query=query, context=context)


openai_service = OpenAIService()

