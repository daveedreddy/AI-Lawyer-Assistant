import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.services.history_service import history_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["History"])


class CreateSessionRequest(BaseModel):
    title: str = Field(default="New Question", max_length=160)


class AddMessageRequest(BaseModel):
    role: str
    content: str = Field(..., min_length=1)
    citations: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class UpdateTitleRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)


def _persistence_error(exc: RuntimeError) -> HTTPException:
    return HTTPException(status_code=503, detail=str(exc))


@router.post("/", summary="Create a new chat session")
async def create_session(
    body: CreateSessionRequest = Body(default=CreateSessionRequest()),
    user_id: str = Depends(get_current_user),
):
    try:
        return history_service.create_session(user_id=user_id, title=body.title)
    except RuntimeError as exc:
        raise _persistence_error(exc) from exc


@router.get("/", summary="List chat sessions for the current user")
async def get_sessions(user_id: str = Depends(get_current_user)):
    try:
        return history_service.get_all_sessions(user_id=user_id)
    except RuntimeError as exc:
        raise _persistence_error(exc) from exc


@router.get("/{session_id}", summary="Get a session with all its messages")
async def get_session(
    session_id: str = Path(...),
    user_id: str = Depends(get_current_user),
):
    try:
        session = history_service.get_session(session_id=session_id, user_id=user_id)
    except RuntimeError as exc:
        raise _persistence_error(exc) from exc

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


@router.patch("/{session_id}", summary="Rename a chat session")
async def update_title(
    session_id: str = Path(...),
    body: UpdateTitleRequest = Body(...),
    user_id: str = Depends(get_current_user),
):
    try:
        success = history_service.update_session_title(
            session_id=session_id,
            title=body.title,
            user_id=user_id,
        )
    except RuntimeError as exc:
        raise _persistence_error(exc) from exc

    if not success:
        raise HTTPException(status_code=404, detail="Session not found or update failed.")
    return {"message": "Title updated successfully."}


@router.delete("/{session_id}", summary="Delete a chat session and all its messages")
async def delete_session(
    session_id: str = Path(...),
    user_id: str = Depends(get_current_user),
):
    try:
        success = history_service.delete_session(session_id=session_id, user_id=user_id)
    except RuntimeError as exc:
        raise _persistence_error(exc) from exc

    if not success:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"message": "Session deleted successfully."}


@router.post("/{session_id}/message", summary="Add a message to a session")
async def add_message(
    session_id: str = Path(...),
    body: AddMessageRequest = Body(...),
    user_id: str = Depends(get_current_user),
):
    try:
        return history_service.add_message(
            session_id=session_id,
            role=body.role,
            content=body.content,
            user_id=user_id,
            citations=body.citations,
            confidence=body.confidence,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise _persistence_error(exc) from exc


@router.delete(
    "/{session_id}/message/{message_id}",
    summary="Delete a specific message from a session",
)
async def delete_message(
    session_id: str = Path(...),
    message_id: str = Path(...),
    user_id: str = Depends(get_current_user),
):
    try:
        success = history_service.delete_message(
            message_id=message_id,
            session_id=session_id,
            user_id=user_id,
        )
    except RuntimeError as exc:
        raise _persistence_error(exc) from exc

    if not success:
        raise HTTPException(status_code=404, detail="Message not found.")
    return {"message": "Message deleted successfully."}
