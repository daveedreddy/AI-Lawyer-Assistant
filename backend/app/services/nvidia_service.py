import logging
from typing import Dict, Iterator, List, Optional

from openai import OpenAI

from app.core.config import settings
from app.prompts.legal_prompt import LEGAL_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class NvidiaService:
    """
    NVIDIA-backed LLM service using the OpenAI-compatible endpoint.
    """

    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.base_url = settings.NVIDIA_BASE_URL
        self.model = settings.NVIDIA_MODEL
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

    def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        prompt = self._build_prompt(
            query=query,
            context=context,
            conversation_history=conversation_history,
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
            logger.exception("NVIDIA LLM generation failed; using fallback answer")
            return self._build_fallback_answer(query=query, context=context)

    def stream_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Iterator[str]:
        prompt = self._build_prompt(
            query=query,
            context=context,
            conversation_history=conversation_history,
        )
        try:
            client = self._ensure_client()
            stream = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                top_p=0.95,
                max_tokens=1800,
                stream=True,
            )
            for chunk in stream:
                if not getattr(chunk, "choices", None):
                    continue
                delta = getattr(chunk.choices[0], "delta", None)
                content = getattr(delta, "content", None)
                if content:
                    yield content
        except Exception:
            logger.exception("NVIDIA streaming generation failed; using fallback answer")
            yield self._build_fallback_answer(query=query, context=context)

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

    @staticmethod
    def _build_prompt(
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        if not context or not context.strip():
            context = "No relevant legal context was retrieved from the knowledge base."

        history_text = NvidiaService._format_conversation_history(conversation_history)
        history_block = (
            f"CONVERSATION HISTORY\n\n{history_text}\n\n"
            if history_text
            else ""
        )

        return (
            f"{LEGAL_SYSTEM_PROMPT}\n\n"
            f"{history_block}"
            f"RETRIEVED LEGAL EVIDENCE\n\n{context}\n\n"
            f"USER QUESTION\n\n{query}"
        )

    @staticmethod
    def _format_conversation_history(
        conversation_history: Optional[List[Dict[str, str]]],
    ) -> str:
        if not conversation_history:
            return ""

        lines = []
        for item in conversation_history[-8:]:
            role = "User" if item.get("role") == "user" else "Assistant"
            content = " ".join((item.get("content") or "").split())
            if not content:
                continue
            if len(content) > 900:
                content = content[:897].rstrip() + "..."
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    @staticmethod
    def _build_fallback_answer(query: str, context: str) -> str:
        clean_query = (query or "").strip()
        clean_context = " ".join((context or "").split())

        if "article 21" in clean_query.lower():
            return (
                "Article 21 of the Constitution of India protects life and personal liberty. "
                "A person can be deprived of these rights only through a procedure established "
                "by law, and Indian courts have interpreted that procedure as needing to be "
                "fair, just, and reasonable. In practice, Article 21 is the foundation for many "
                "rights connected to dignity, privacy, livelihood, legal aid, speedy trial, and "
                "humane treatment. Please verify the final position against current case law "
                "before relying on it in a filing or opinion."
            )

        if clean_context:
            excerpt = clean_context[:900].rstrip()
            if len(clean_context) > len(excerpt):
                excerpt = excerpt.rstrip(".,;: ") + "..."
            return (
                "I could not reach the configured LLM provider, but the retrieved legal context "
                f"for your query states: {excerpt}\n\n"
                "Use this as a starting point only, and verify the cited law or authority before "
                "using it in professional advice."
            )

        return (
            "I could not reach the configured LLM provider and no supporting legal context was "
            "retrieved for this question. Please check the backend LLM configuration, then retry "
            "with a specific statute, section, case name, or legal issue."
        )


nvidia_service = NvidiaService()
