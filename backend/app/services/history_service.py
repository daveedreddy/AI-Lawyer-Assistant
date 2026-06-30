"""
History Service — Supabase PostgreSQL backed.

All methods degrade gracefully when Supabase is not yet configured
(SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing from .env).
In that state, read operations return empty lists and write operations
log a warning and no-op — the AI chat still works, persistence does not.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.database.supabase_client import get_supabase
from app.models.history_models import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _map_session(row: Dict[str, Any], messages: List[Dict[str, Any]] = None) -> ChatSession:
    return ChatSession(
        session_id=row["id"],
        user_id=row.get("user_id"),
        title=row.get("title", "Untitled"),
        summary=row.get("summary"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        messages=[_map_message(m) for m in (messages or [])],
    )


def _map_message(row: Dict[str, Any]) -> ChatMessage:
    citations = row.get("citations_json") or []
    if isinstance(citations, str):
        try:
            citations = json.loads(citations)
        except Exception:
            citations = []
    return ChatMessage(
        id=row.get("id"),
        role=row.get("role", "user"),
        content=row.get("content", ""),
        citations=citations,
        confidence=row.get("confidence"),
        timestamp=row["created_at"],
    )


class HistoryService:

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def create_session(self, user_id: Optional[str], title: str = "New Consultation") -> ChatSession:
        sb = get_supabase()
        if not sb:
            logger.warning("Supabase not configured — session not persisted.")
            now = _now()
            return ChatSession(
                session_id=str(uuid4()),
                user_id=user_id,
                title=title,
                messages=[],
                created_at=now,
                updated_at=now,
            )

        now = _now()
        data = {
            "id": str(uuid4()),
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
        }
        result = sb.table("chat_sessions").insert(data).execute()
        row = result.data[0] if result.data else data
        return _map_session(row)

    def get_all_sessions(self, user_id: Optional[str]) -> List[ChatSession]:
        sb = get_supabase()
        if not sb:
            logger.warning("Supabase not configured — returning empty session list.")
            return []

        query = sb.table("chat_sessions").select("*").order("updated_at", desc=True)
        if user_id:
            query = query.eq("user_id", user_id)
        result = query.execute()
        return [_map_session(row) for row in (result.data or [])]

    def get_session(self, session_id: str, user_id: Optional[str] = None) -> Optional[ChatSession]:
        sb = get_supabase()
        if not sb:
            return None

        query = sb.table("chat_sessions").select("*").eq("id", session_id)
        if user_id:
            query = query.eq("user_id", user_id)
        session_result = query.single().execute()
        if not session_result.data:
            return None

        msgs_result = (
            sb.table("chat_messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )
        return _map_session(session_result.data, msgs_result.data or [])

    def delete_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        sb = get_supabase()
        if not sb:
            logger.warning("Supabase not configured — delete skipped.")
            return False

        query = sb.table("chat_sessions").delete().eq("id", session_id)
        if user_id:
            query = query.eq("user_id", user_id)
        query.execute()
        return True

    def update_session_title(self, session_id: str, title: str, user_id: Optional[str] = None) -> bool:
        sb = get_supabase()
        if not sb:
            return False

        query = (
            sb.table("chat_sessions")
            .update({"title": title, "updated_at": _now()})
            .eq("id", session_id)
        )
        if user_id:
            query = query.eq("user_id", user_id)
        query.execute()
        return True

    def touch_session(self, session_id: str) -> None:
        sb = get_supabase()
        if not sb:
            return
        sb.table("chat_sessions").update({"updated_at": _now()}).eq("id", session_id).execute()

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[Dict[str, Any]]] = None,
        confidence: Optional[float] = None,
    ) -> ChatMessage:
        sb = get_supabase()
        now = _now()

        if not sb:
            logger.warning("Supabase not configured — message not persisted.")
            return ChatMessage(
                id=str(uuid4()),
                role=role,
                content=content,
                citations=citations or [],
                confidence=confidence,
                timestamp=now,
            )

        data = {
            "id": str(uuid4()),
            "session_id": session_id,
            "role": role,
            "content": content,
            "citations_json": json.dumps(citations or []),
            "confidence": confidence,
            "created_at": now,
        }
        result = sb.table("chat_messages").insert(data).execute()
        row = result.data[0] if result.data else data
        self.touch_session(session_id)
        return _map_message(row)

    def delete_message(self, message_id: str, session_id: str) -> bool:
        sb = get_supabase()
        if not sb:
            return False
        sb.table("chat_messages").delete().eq("id", message_id).eq("session_id", session_id).execute()
        return True

    # ------------------------------------------------------------------
    # Title generation
    # ------------------------------------------------------------------

    @staticmethod
    def generate_title(first_user_message: str) -> str:
        """Derives a short session title from the first user message."""
        text = first_user_message.strip()
        if len(text) <= 60:
            return text.rstrip("?.,!")
        # Take first sentence or first 60 chars
        for delimiter in [".", "?", "!"]:
            idx = text.find(delimiter)
            if 0 < idx <= 60:
                return text[:idx]
        return text[:57].rstrip() + "..."

    # ------------------------------------------------------------------
    # User Stats
    # ------------------------------------------------------------------

    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        sb = get_supabase()
        if not sb:
            return {"total_chats": 0, "documents_analyzed": 0, "drafts_generated": 0, "saved_citations": 0}

        sessions = sb.table("chat_sessions").select("id", count="exact").eq("user_id", user_id).execute()
        docs = sb.table("uploaded_documents").select("id", count="exact").eq("user_id", user_id).execute()
        citations_count = sb.table("chat_messages").select("id", count="exact").eq(
            "session_id",
            sb.table("chat_sessions").select("id").eq("user_id", user_id)
        ).execute()

        return {
            "total_chats": sessions.count or 0,
            "documents_analyzed": docs.count or 0,
            "drafts_generated": 0,
            "saved_citations": 0,
        }


history_service = HistoryService()