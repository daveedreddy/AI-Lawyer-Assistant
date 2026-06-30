import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import BaseModel

from app.core.auth import get_optional_user
from app.services.history_service import history_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["History"])


# ── Request / Response schemas ──────────────────────────────────────────────

class CreateSessionRequest(BaseModel):
    title: str = "New Consultation"


class AddMessageRequest(BaseModel):
    role: str  # "user" | "ai"
    content: str
    citations: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None


class UpdateTitleRequest(BaseModel):
    title: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/", summary="Create a new chat session")
async def create_session(
    body: CreateSessionRequest = Body(default=CreateSessionRequest()),
    user_id: Optional[str] = Depends(get_optional_user),
):
    return history_service.create_session(user_id=user_id, title=body.title)


@router.get("/", summary="List all chat sessions for the current user")
async def get_sessions(
    user_id: Optional[str] = Depends(get_optional_user),
):
    return history_service.get_all_sessions(user_id=user_id)


@router.get("/{session_id}", summary="Get a session with all its messages")
async def get_session(
    session_id: str = Path(...),
    user_id: Optional[str] = Depends(get_optional_user),
):
    session = history_service.get_session(session_id=session_id, user_id=user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


@router.patch("/{session_id}", summary="Rename a chat session")
async def update_title(
    session_id: str = Path(...),
    body: UpdateTitleRequest = Body(...),
    user_id: Optional[str] = Depends(get_optional_user),
):
    success = history_service.update_session_title(
        session_id=session_id, title=body.title, user_id=user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or update failed.")
    return {"message": "Title updated successfully."}


@router.delete("/{session_id}", summary="Delete a chat session and all its messages")
async def delete_session(
    session_id: str = Path(...),
    user_id: Optional[str] = Depends(get_optional_user),
):
    success = history_service.delete_session(session_id=session_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"message": "Session deleted successfully."}


@router.post("/{session_id}/message", summary="Add a message to a session")
async def add_message(
    session_id: str = Path(...),
    body: AddMessageRequest = Body(...),
    user_id: Optional[str] = Depends(get_optional_user),
):
    message = history_service.add_message(
        session_id=session_id,
        role=body.role,
        content=body.content,
        citations=body.citations,
        confidence=body.confidence,
    )
    return message


@router.delete(
    "/{session_id}/message/{message_id}",
    summary="Delete a specific message from a session",
)
async def delete_message(
    session_id: str = Path(...),
    message_id: str = Path(...),
    user_id: Optional[str] = Depends(get_optional_user),
):
    success = history_service.delete_message(
        message_id=message_id, session_id=session_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Message not found.")
    return {"message": "Message deleted successfully."}