import logging
import os

from openai import OpenAI

from app.prompts.legal_prompt import LEGAL_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class NvidiaService:
    """
    NVIDIA-backed LLM service using the OpenAI-compatible endpoint.
    """

    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
        self.client = None

        if self.api_key:
            logger.info("NVIDIA service configured with model %s", self.model)
        else:
            logger.warning(
                "NVIDIA_API_KEY is not set. LLM calls will fail until it is configured."
            )

    def _ensure_client(self) -> OpenAI:
        if not self.api_key:
            raise RuntimeError(
                "NVIDIA_API_KEY is not configured. "
                "Set the NVIDIA_API_KEY environment variable."
            )
        if self.client is None:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self.client

    def generate_response(self, query: str, context: str) -> str:
        if not context or not context.strip():
            context = "No relevant legal context was retrieved from the knowledge base."

        prompt = (
            f"{LEGAL_SYSTEM_PROMPT}\n\n"
            f"RETRIEVED LEGAL EVIDENCE\n\n{context}\n\n"
            f"USER QUESTION\n\n{query}"
        )

        try:
            client = self._ensure_client()
            completion = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                top_p=0.95,
                max_tokens=1800,
                stream=False,
            )

            answer = ""
            if getattr(completion, "choices", None):
                answer = completion.choices[0].message.content or ""

            answer = answer.strip()
            if not answer:
                raise RuntimeError("NVIDIA returned an empty response.")
            return answer

        except Exception:
            logger.exception("NVIDIA LLM generation failed")
            raise

    def generate_raw(self, prompt: str, max_tokens: int = 800) -> str:
        """
        Send a raw prompt to the LLM without the legal system prompt.
        Used for document analysis tasks.
        """
        try:
            client = self._ensure_client()
            completion = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                top_p=0.95,
                max_tokens=max_tokens,
                stream=False,
            )
            answer = ""
            if getattr(completion, "choices", None):
                answer = completion.choices[0].message.content or ""
            return answer.strip()
        except Exception:
            logger.exception("NVIDIA raw generation failed")
            raise


nvidia_service = NvidiaService()
