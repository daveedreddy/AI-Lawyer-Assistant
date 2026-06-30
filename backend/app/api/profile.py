"""
Profile API — user profile, stats, and settings.
All endpoints use optional auth (degrade gracefully without Supabase).
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from app.core.auth import get_optional_user
from app.database.supabase_client import get_supabase
from app.services.history_service import history_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["Profile"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class UserProfileResponse(BaseModel):
    id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    bar_enrollment: Optional[str] = None
    practice_areas: List[str] = []
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


class UpdateSettingsRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    model_preference: Optional[str] = None
    notifications_enabled: Optional[bool] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_profile_row(user_id: str) -> Optional[Dict[str, Any]]:
    sb = get_supabase()
    if not sb:
        return None
    try:
        result = sb.table("user_profiles").select("*").eq("id", user_id).maybe_single().execute()
        return result.data
    except Exception as exc:
        logger.error("Failed to fetch profile: %s", exc)
        return None


def _get_settings_row(user_id: str) -> Optional[Dict[str, Any]]:
    sb = get_supabase()
    if not sb:
        return None
    try:
        result = sb.table("user_settings").select("*").eq("user_id", user_id).maybe_single().execute()
        return result.data
    except Exception as exc:
        logger.error("Failed to fetch settings: %s", exc)
        return None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=UserProfileResponse)
async def get_profile(user_id: Optional[str] = Depends(get_optional_user)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    row = _get_profile_row(user_id)
    if not row:
        return UserProfileResponse(id=user_id)
    return UserProfileResponse(
        id=user_id,
        email=row.get("email"),
        full_name=row.get("full_name"),
        bar_enrollment=row.get("bar_enrollment"),
        practice_areas=row.get("practice_areas") or [],
        location=row.get("location"),
        avatar_url=row.get("avatar_url"),
    )


@router.patch("/", response_model=UserProfileResponse)
async def update_profile(
    body: UpdateProfileRequest = Body(...),
    user_id: Optional[str] = Depends(get_optional_user),
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    sb = get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database not configured.")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update.")

    try:
        sb.table("user_profiles").upsert({"id": user_id, **updates}).execute()
    except Exception as exc:
        logger.error("Profile update failed: %s", exc)
        raise HTTPException(status_code=500, detail="Profile update failed.")

    row = _get_profile_row(user_id) or {}
    return UserProfileResponse(
        id=user_id,
        email=row.get("email"),
        full_name=row.get("full_name"),
        bar_enrollment=row.get("bar_enrollment"),
        practice_areas=row.get("practice_areas") or [],
        location=row.get("location"),
        avatar_url=row.get("avatar_url"),
    )


@router.get("/stats", response_model=UserStatsResponse)
async def get_stats(user_id: Optional[str] = Depends(get_optional_user)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    stats = history_service.get_user_stats(user_id)
    return UserStatsResponse(**stats)


@router.get("/settings", response_model=UserSettingsResponse)
async def get_settings(user_id: Optional[str] = Depends(get_optional_user)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    row = _get_settings_row(user_id)
    if not row:
        return UserSettingsResponse()
    return UserSettingsResponse(
        theme=row.get("theme", "dark"),
        language=row.get("language", "en"),
        model_preference=row.get("model_preference", "nvidia"),
        notifications_enabled=row.get("notifications_enabled", True),
    )


@router.patch("/settings", response_model=UserSettingsResponse)
async def update_settings(
    body: UpdateSettingsRequest = Body(...),
    user_id: Optional[str] = Depends(get_optional_user),
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    sb = get_supabase()
    if not sb:
        raise HTTPException(status_code=503, detail="Database not configured.")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    updates["user_id"] = user_id

    try:
        sb.table("user_settings").upsert(updates).execute()
    except Exception as exc:
        logger.error("Settings update failed: %s", exc)
        raise HTTPException(status_code=500, detail="Settings update failed.")

    row = _get_settings_row(user_id) or {}
    return UserSettingsResponse(
        theme=row.get("theme", "dark"),
        language=row.get("language", "en"),
        model_preference=row.get("model_preference", "nvidia"),
        notifications_enabled=row.get("notifications_enabled", True),
    )
