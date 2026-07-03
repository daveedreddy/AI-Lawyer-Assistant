import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator

from app.core.auth import get_optional_user
from app.core.config import settings
from app.core.exceptions import APIException
from app.orchestrator.query_orchestrator import query_orchestrator
from app.services.history_service import history_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Lawyer"])


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=settings.MAX_QUERY_LENGTH)
    top_k: int = Field(default=5, ge=1, le=10)
    session_id: Optional[str] = Field(default=None)

    @field_validator("query")
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query cannot be empty")
        return value


def _conversation_history_from_session(session) -> List[Dict[str, str]]:
    return [
        {"role": message.role, "content": message.content}
        for message in session.messages
        if message.content and message.content.strip()
    ]


@router.post("/", summary="Send a legal query and receive an AI response")
async def chat(
    request: ChatRequest,
    user_id: Optional[str] = Depends(get_optional_user),
):
    try:
        session_id = request.session_id
        session = None
        conversation_history: List[Dict[str, str]] = []

        # 1. Load existing messages so follow-up questions can use prior context.
        if session_id:
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication is required to save and continue chat history.",
                )

            try:
                session = history_service.get_session(session_id, user_id)
            except RuntimeError as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc

            if session is None:
                raise HTTPException(status_code=404, detail="Session not found.")

            conversation_history = _conversation_history_from_session(session)

            try:
                history_service.add_message(
                    session_id=session_id,
                    role="user",
                    content=request.query,
                    user_id=user_id,
                )
            except PermissionError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except RuntimeError as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc

        # 2. Process query through RAG pipeline
        response = query_orchestrator.process_query(
            query=request.query,
            top_k=request.top_k,
            conversation_history=conversation_history,
        )

        # 3. Auto-generate session title from first user message
        if session_id and user_id and session:
            try:
                if session.title in ("New Consultation", ""):
                    new_title = history_service.generate_title(request.query)
                    history_service.update_session_title(session_id, new_title, user_id)
            except RuntimeError as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc

        # 4. Build sources list from citations
        sources = [c["url"] for c in response.citations if c.get("url")]

        # 5. Persist AI response to history
        if session_id and user_id:
            try:
                history_service.add_message(
                    session_id=session_id,
                    role="ai",
                    content=response.answer,
                    user_id=user_id,
                    citations=response.citations,
                    confidence=response.confidence,
                )
            except PermissionError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except RuntimeError as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc

        result = response.model_dump()
        result["sources"] = sources
        result["session_id"] = session_id
        return result

    except HTTPException:
        raise
    except APIException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Chat endpoint error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
