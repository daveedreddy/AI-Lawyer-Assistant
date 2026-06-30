import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator

from app.core.auth import get_optional_user
from app.core.config import settings
from app.core.exceptions import APIException
from app.models.response_models import QueryResponse, RetrievedDocument
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


@router.post("/", summary="Send a legal query and receive an AI response")
async def chat(
    request: ChatRequest,
    user_id: Optional[str] = Depends(get_optional_user),
):
    try:
        # 1. Persist user message to history (if session provided)
        session_id = request.session_id
        if session_id:
            try:
                history_service.add_message(
                    session_id=session_id,
                    role="user",
                    content=request.query,
                )
            except Exception as exc:
                logger.warning("Could not persist user message: %s", exc)

        # 2. Process query through RAG pipeline
        response = query_orchestrator.process_query(
            query=request.query,
            top_k=request.top_k,
        )

        # 3. Auto-generate session title from first user message
        if session_id:
            try:
                session = history_service.get_session(session_id, user_id)
                if session and session.title in ("New Consultation", ""):
                    new_title = history_service.generate_title(request.query)
                    history_service.update_session_title(session_id, new_title, user_id)
            except Exception as exc:
                logger.warning("Could not auto-title session: %s", exc)

        # 4. Build sources list from citations
        sources = [c["url"] for c in response.citations if c.get("url")]

        # 5. Persist AI response to history
        if session_id:
            try:
                history_service.add_message(
                    session_id=session_id,
                    role="ai",
                    content=response.answer,
                    citations=response.citations,
                    confidence=response.confidence,
                )
            except Exception as exc:
                logger.warning("Could not persist AI message: %s", exc)

        result = response.model_dump()
        result["sources"] = sources
        result["session_id"] = session_id
        return result

    except APIException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Chat endpoint error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc