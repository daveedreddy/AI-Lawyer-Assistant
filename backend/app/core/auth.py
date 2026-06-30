import logging
import os
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

_security = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> dict:
    """
    Decode and verify a Supabase-issued JWT.
    Supabase uses HS256 signed with SUPABASE_JWT_SECRET.
    """
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        raise HTTPException(
            status_code=503,
            detail="Authentication service not configured. Set SUPABASE_JWT_SECRET.",
        )
    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(_security),
) -> str:
    """Require a valid Supabase JWT — returns user_id (sub claim)."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required.")
    payload = _decode_token(credentials.credentials)
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject claim.")
    return user_id


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Security(_security),
) -> Optional[str]:
    """
    Optionally extract user_id from a JWT.
    Returns None if no token is present or credentials are not yet configured.
    Never raises — used for endpoints that degrade gracefully without auth.
    """
    if not credentials:
        return None
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        return None
    try:
        payload = _decode_token(credentials.credentials)
        return payload.get("sub")
    except Exception:
        return None
