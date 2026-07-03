import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.database.supabase_client import require_supabase
from app.services.history_service import history_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["Profile"])


class UserProfileResponse(BaseModel):
    id: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    bar_enrollment: Optional[str] = None
    practice_areas: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    avatar_url: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    bar_enrollment: Optional[str] = None
    practice_areas: Optional[List[str]] = None
    location: Optional[str] = None


class UserStatsResponse(BaseModel):
    total_chats: int = 0
    documents_analyzed: int = 0
    drafts_generated: int = 0
    saved_citations: int = 0


class UserSettingsResponse(BaseModel):
    theme: str = "dark"
    language: str = "en"
    model_preference: str = "nvidia"
    notifications_enabled: bool = True
    temperature: float = 0.3
    api_base_url: Optional[str] = None


class UpdateSettingsRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    model_preference: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    api_base_url: Optional[str] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_profile_row(user_id: str) -> Optional[Dict[str, Any]]:
    sb = require_supabase()
    result = sb.table("user_profiles").select("*").eq("id", user_id).maybe_single().execute()
    return result.data


def _get_settings_row(user_id: str) -> Optional[Dict[str, Any]]:
    sb = require_supabase()
    result = sb.table("user_settings").select("*").eq("user_id", user_id).maybe_single().execute()
    return result.data


def _profile_response(user_id: str, row: Optional[Dict[str, Any]]) -> UserProfileResponse:
    row = row or {}
    return UserProfileResponse(
        id=user_id,
        email=row.get("email"),
        full_name=row.get("full_name"),
        bar_enrollment=row.get("bar_enrollment"),
        practice_areas=row.get("practice_areas") or [],
        location=row.get("location"),
        avatar_url=row.get("avatar_url"),
    )


def _settings_response(row: Optional[Dict[str, Any]]) -> UserSettingsResponse:
    row = row or {}
    return UserSettingsResponse(
        theme=row.get("theme", "dark"),
        language=row.get("language", "en"),
        model_preference=row.get("model_preference", "nvidia"),
        notifications_enabled=row.get("notifications_enabled", True),
        temperature=float(row.get("temperature", 0.3)),
        api_base_url=row.get("api_base_url"),
    )


@router.get("/", response_model=UserProfileResponse)
async def get_profile(user_id: str = Depends(get_current_user)):
    try:
        return _profile_response(user_id, _get_profile_row(user_id))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.patch("/", response_model=UserProfileResponse)
async def update_profile(
    body: UpdateProfileRequest = Body(...),
    user_id: str = Depends(get_current_user),
):
    updates = {key: value for key, value in body.model_dump().items() if value is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update.")

    try:
        sb = require_supabase()
        updates["id"] = user_id
        updates["updated_at"] = _now()
        sb.table("user_profiles").upsert(updates, on_conflict="id").execute()
        return _profile_response(user_id, _get_profile_row(user_id))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Profile update failed")
        raise HTTPException(status_code=500, detail="Profile update failed.") from exc


@router.get("/stats", response_model=UserStatsResponse)
async def get_stats(user_id: str = Depends(get_current_user)):
    try:
        return UserStatsResponse(**history_service.get_user_stats(user_id))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/settings", response_model=UserSettingsResponse)
async def get_settings(user_id: str = Depends(get_current_user)):
    try:
        return _settings_response(_get_settings_row(user_id))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.patch("/settings", response_model=UserSettingsResponse)
async def update_settings(
    body: UpdateSettingsRequest = Body(...),
    user_id: str = Depends(get_current_user),
):
    updates = {key: value for key, value in body.model_dump().items() if value is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update.")

    try:
        sb = require_supabase()
        updates["user_id"] = user_id
        updates["updated_at"] = _now()
        sb.table("user_settings").upsert(updates, on_conflict="user_id").execute()
        return _settings_response(_get_settings_row(user_id))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Settings update failed")
        raise HTTPException(status_code=500, detail="Settings update failed.") from exc
