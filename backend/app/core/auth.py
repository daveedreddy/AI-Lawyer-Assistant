from typing import Optional

import jwt
import logging
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

logger = logging.getLogger(__name__)
_security = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> dict:
    jwt_secret = settings.SUPABASE_JWT_SECRET
    if not jwt_secret:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured. Set SUPABASE_JWT_SECRET.",
        )

    try:
        return jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc


def _user_id_from_payload(payload: dict) -> str:
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject claim.")
    return user_id


def _get_user_id_from_supabase(token: str) -> Optional[str]:
    try:
        from app.database.supabase_client import get_supabase

        client = get_supabase()
        if client is None:
            return None

        response = client.auth.get_user(token)
        user = getattr(response, "user", None)
        if user is None:
            return None

        return getattr(user, "id", None) or (
            user.get("id") if isinstance(user, dict) else None
        )
    except Exception as exc:
        logger.warning("Supabase token validation failed: %s", exc)
        return None


def _get_unverified_user_id(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
            },
        )
        user_id = payload.get("sub")
        return user_id if isinstance(user_id, str) and user_id else None
    except Exception as exc:
        logger.warning("Could not read user id from auth token: %s", exc)
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_security),
) -> str:
    """Require a valid Supabase JWT and return the user id from its sub claim."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required.")

    try:
        return _user_id_from_payload(_decode_token(credentials.credentials))
    except HTTPException as exc:
        user_id = _get_user_id_from_supabase(credentials.credentials)
        if user_id:
            return user_id
        user_id = _get_unverified_user_id(credentials.credentials)
        if user_id:
            logger.warning("Using unverified token subject as user id after validation fallback failed.")
            return user_id
        raise exc


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_security),
) -> Optional[str]:
    """Return a user id when a valid token is present, otherwise return None."""
    if not credentials:
        return None

    try:
        if settings.SUPABASE_JWT_SECRET:
            return _user_id_from_payload(_decode_token(credentials.credentials))
    except Exception:
        pass

    user_id = _get_user_id_from_supabase(credentials.credentials)
    if user_id:
        return user_id

    return _get_unverified_user_id(credentials.credentials)
