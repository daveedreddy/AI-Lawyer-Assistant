import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def get_supabase():
    """
    Returns a Supabase Python client (service-role key).
    Returns None and logs a warning if credentials are not yet configured.
    """
    global _client

    if _client is not None:
        return _client

    if not settings.supabase_ready:
        logger.warning(
            "Supabase credentials not configured. "
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env. "
            "Database persistence is disabled until then."
        )
        return None

    try:
        from supabase import create_client
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        logger.info("Supabase client initialized successfully.")
        return _client
    except Exception as exc:
        logger.error("Failed to initialize Supabase client: %s", exc)
        return None


def require_supabase():
    client = get_supabase()
    if client is None:
        raise RuntimeError(
            "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )
    return client
