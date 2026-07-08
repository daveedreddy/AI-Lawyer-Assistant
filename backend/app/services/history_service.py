import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.database.supabase_client import require_supabase
from app.models.history_models import ChatMessage, ChatSession

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[2]
LOCAL_HISTORY_PATH = BACKEND_DIR / "database" / "local_history.json"
_local_lock = Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _map_message(row: Dict[str, Any]) -> ChatMessage:
    citations = row.get("citations_json") or []
    return ChatMessage(
        id=row.get("id"),
        role=row.get("role", "user"),
        content=row.get("content", ""),
        citations=citations if isinstance(citations, list) else [],
        confidence=row.get("confidence"),
        timestamp=row["created_at"],
    )


def _map_session(
    row: Dict[str, Any],
    messages: Optional[List[Dict[str, Any]]] = None,
) -> ChatSession:
    return ChatSession(
        session_id=row["id"],
        user_id=row.get("user_id"),
        title=row.get("title") or "Untitled",
        summary=row.get("summary"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        messages=[_map_message(message) for message in (messages or [])],
    )


def _empty_local_store() -> Dict[str, List[Dict[str, Any]]]:
    return {"chat_sessions": [], "chat_messages": []}


def _read_local_store() -> Dict[str, List[Dict[str, Any]]]:
    LOCAL_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOCAL_HISTORY_PATH.exists():
        return _empty_local_store()

    try:
        with LOCAL_HISTORY_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        logger.exception("Local history store is unreadable; starting with an empty store.")
        return _empty_local_store()

    if not isinstance(data, dict):
        return _empty_local_store()

    return {
        "chat_sessions": data.get("chat_sessions") or [],
        "chat_messages": data.get("chat_messages") or [],
    }


def _write_local_store(data: Dict[str, List[Dict[str, Any]]]) -> None:
    LOCAL_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = LOCAL_HISTORY_PATH.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temp_path.replace(LOCAL_HISTORY_PATH)


class HistoryService:
    def _warn_local_fallback(self, exc: Exception) -> None:
        logger.warning("Supabase chat history unavailable; using local history store: %s", exc)

    def _create_session_local(self, row: Dict[str, Any]) -> ChatSession:
        with _local_lock:
            data = _read_local_store()
            data["chat_sessions"].append(row)
            _write_local_store(data)
        return _map_session(row)

    def create_session(self, user_id: str, title: str = "New Question") -> ChatSession:
        now = _now()
        row = {
            "id": str(uuid4()),
            "user_id": user_id,
            "title": title.strip() or "New Question",
            "created_at": now,
            "updated_at": now,
        }

        try:
            sb = require_supabase()
            result = sb.table("chat_sessions").insert(row).execute()
            return _map_session(result.data[0] if result.data else row)
        except Exception as exc:
            self._warn_local_fallback(exc)
            return self._create_session_local(row)

    def _get_all_sessions_local(self, user_id: str) -> List[ChatSession]:
        with _local_lock:
            data = _read_local_store()

        rows = [
            row
            for row in data["chat_sessions"]
            if row.get("user_id") == user_id
        ]
        rows.sort(key=lambda row: row.get("updated_at", ""), reverse=True)
        return [_map_session(row) for row in rows]

    def get_all_sessions(self, user_id: str) -> List[ChatSession]:
        try:
            sb = require_supabase()
            result = (
                sb.table("chat_sessions")
                .select("*")
                .eq("user_id", user_id)
                .order("updated_at", desc=True)
                .execute()
            )
            return [_map_session(row) for row in (result.data or [])]
        except Exception as exc:
            self._warn_local_fallback(exc)
            return self._get_all_sessions_local(user_id)

    def _get_session_local(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        with _local_lock:
            data = _read_local_store()

        session = next(
            (
                row
                for row in data["chat_sessions"]
                if row.get("id") == session_id and row.get("user_id") == user_id
            ),
            None,
        )
        if not session:
            return None

        messages = [
            row
            for row in data["chat_messages"]
            if row.get("session_id") == session_id
        ]
        messages.sort(key=lambda row: row.get("created_at", ""))
        return _map_session(session, messages)

    def get_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        try:
            sb = require_supabase()
            session_result = (
                sb.table("chat_sessions")
                .select("*")
                .eq("id", session_id)
                .eq("user_id", user_id)
                .maybe_single()
                .execute()
            )
            if not session_result.data:
                return None

            messages_result = (
                sb.table("chat_messages")
                .select("*")
                .eq("session_id", session_id)
                .order("created_at")
                .execute()
            )
            return _map_session(session_result.data, messages_result.data or [])
        except Exception as exc:
            self._warn_local_fallback(exc)
            return self._get_session_local(session_id, user_id)

    def _delete_session_local(self, session_id: str, user_id: str) -> bool:
        with _local_lock:
            data = _read_local_store()
            before = len(data["chat_sessions"])
            data["chat_sessions"] = [
                row
                for row in data["chat_sessions"]
                if not (row.get("id") == session_id and row.get("user_id") == user_id)
            ]
            if len(data["chat_sessions"]) == before:
                return False

            data["chat_messages"] = [
                row for row in data["chat_messages"] if row.get("session_id") != session_id
            ]
            _write_local_store(data)
            return True

    def delete_session(self, session_id: str, user_id: str) -> bool:
        try:
            sb = require_supabase()
            if not self.get_session(session_id, user_id):
                return False

            sb.table("chat_sessions").delete().eq("id", session_id).eq("user_id", user_id).execute()
            return True
        except Exception as exc:
            self._warn_local_fallback(exc)
            return self._delete_session_local(session_id, user_id)

    def _update_session_title_local(self, session_id: str, title: str, user_id: str) -> bool:
        with _local_lock:
            data = _read_local_store()
            for row in data["chat_sessions"]:
                if row.get("id") == session_id and row.get("user_id") == user_id:
                    row["title"] = title
                    row["updated_at"] = _now()
                    _write_local_store(data)
                    return True
        return False

    def update_session_title(self, session_id: str, title: str, user_id: str) -> bool:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Session title cannot be empty.")

        try:
            sb = require_supabase()
            if not self.get_session(session_id, user_id):
                return False

            sb.table("chat_sessions").update(
                {"title": clean_title, "updated_at": _now()}
            ).eq("id", session_id).eq("user_id", user_id).execute()
            return True
        except Exception as exc:
            self._warn_local_fallback(exc)
            return self._update_session_title_local(session_id, clean_title, user_id)

    def _touch_session_local(self, session_id: str, user_id: str) -> None:
        with _local_lock:
            data = _read_local_store()
            for row in data["chat_sessions"]:
                if row.get("id") == session_id and row.get("user_id") == user_id:
                    row["updated_at"] = _now()
                    _write_local_store(data)
                    return

    def touch_session(self, session_id: str, user_id: str) -> None:
        try:
            sb = require_supabase()
            sb.table("chat_sessions").update(
                {"updated_at": _now()}
            ).eq("id", session_id).eq("user_id", user_id).execute()
        except Exception as exc:
            self._warn_local_fallback(exc)
            self._touch_session_local(session_id, user_id)

    def _add_message_local(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: str,
        citations: Optional[List[Dict[str, Any]]] = None,
        confidence: Optional[float] = None,
    ) -> ChatMessage:
        with _local_lock:
            data = _read_local_store()
            session = next(
                (
                    row
                    for row in data["chat_sessions"]
                    if row.get("id") == session_id and row.get("user_id") == user_id
                ),
                None,
            )
            if not session:
                raise PermissionError("Session not found for the current user.")

            row = {
                "id": str(uuid4()),
                "session_id": session_id,
                "role": role,
                "content": content,
                "citations_json": citations or [],
                "confidence": confidence,
                "created_at": _now(),
            }
            data["chat_messages"].append(row)
            session["updated_at"] = _now()
            _write_local_store(data)
            return _map_message(row)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: str,
        citations: Optional[List[Dict[str, Any]]] = None,
        confidence: Optional[float] = None,
    ) -> ChatMessage:
        if role not in {"user", "ai"}:
            raise ValueError("Message role must be 'user' or 'ai'.")
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty.")

        try:
            sb = require_supabase()
            if not self.get_session(session_id, user_id):
                raise PermissionError("Session not found for the current user.")

            row = {
                "id": str(uuid4()),
                "session_id": session_id,
                "role": role,
                "content": content,
                "citations_json": citations or [],
                "confidence": confidence,
                "created_at": _now(),
            }
            result = sb.table("chat_messages").insert(row).execute()
            self.touch_session(session_id, user_id)
            return _map_message(result.data[0] if result.data else row)
        except PermissionError:
            raise
        except Exception as exc:
            self._warn_local_fallback(exc)
            return self._add_message_local(
                session_id=session_id,
                role=role,
                content=content,
                user_id=user_id,
                citations=citations,
                confidence=confidence,
            )

    def _delete_message_local(self, message_id: str, session_id: str, user_id: str) -> bool:
        with _local_lock:
            data = _read_local_store()
            session = next(
                (
                    row
                    for row in data["chat_sessions"]
                    if row.get("id") == session_id and row.get("user_id") == user_id
                ),
                None,
            )
            if not session:
                return False

            before = len(data["chat_messages"])
            data["chat_messages"] = [
                row
                for row in data["chat_messages"]
                if not (row.get("id") == message_id and row.get("session_id") == session_id)
            ]
            if len(data["chat_messages"]) == before:
                return False

            session["updated_at"] = _now()
            _write_local_store(data)
            return True

    def delete_message(self, message_id: str, session_id: str, user_id: str) -> bool:
        try:
            sb = require_supabase()
            if not self.get_session(session_id, user_id):
                return False

            existing = (
                sb.table("chat_messages")
                .select("id")
                .eq("id", message_id)
                .eq("session_id", session_id)
                .maybe_single()
                .execute()
            )
            if not existing.data:
                return False

            sb.table("chat_messages").delete().eq("id", message_id).eq("session_id", session_id).execute()
            self.touch_session(session_id, user_id)
            return True
        except Exception as exc:
            self._warn_local_fallback(exc)
            return self._delete_message_local(message_id, session_id, user_id)

    @staticmethod
    def generate_title(first_user_message: str) -> str:
        text = first_user_message.strip()
        if len(text) <= 60:
            return text.rstrip("?.,!") or "New Question"

        for delimiter in [".", "?", "!"]:
            idx = text.find(delimiter)
            if 0 < idx <= 60:
                return text[:idx].strip()
        return text[:57].rstrip() + "..."

    def _get_user_stats_local(self, user_id: str) -> Dict[str, int]:
        sessions = self._get_all_sessions_local(user_id)
        session_ids = {session.session_id for session in sessions}

        with _local_lock:
            data = _read_local_store()

        drafts_generated = 0
        saved_citations = 0
        for message in data["chat_messages"]:
            if message.get("session_id") not in session_ids:
                continue
            if message.get("role") == "ai":
                drafts_generated += 1
            citations = message.get("citations_json") or []
            if isinstance(citations, list):
                saved_citations += len(citations)

        return {
            "total_chats": len(sessions),
            "documents_analyzed": 0,
            "drafts_generated": drafts_generated,
            "saved_citations": saved_citations,
        }

    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        try:
            sb = require_supabase()

            sessions = (
                sb.table("chat_sessions")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .execute()
            )
            docs = (
                sb.table("uploaded_documents")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .execute()
            )

            session_ids = [row["id"] for row in (sessions.data or [])]
            drafts_generated = 0
            saved_citations = 0

            if session_ids:
                messages = (
                    sb.table("chat_messages")
                    .select("role,citations_json")
                    .in_("session_id", session_ids)
                    .execute()
                )
                for message in messages.data or []:
                    if message.get("role") == "ai":
                        drafts_generated += 1
                    citations = message.get("citations_json") or []
                    if isinstance(citations, list):
                        saved_citations += len(citations)

            return {
                "total_chats": sessions.count or 0,
                "documents_analyzed": docs.count or 0,
                "drafts_generated": drafts_generated,
                "saved_citations": saved_citations,
            }
        except Exception as exc:
            self._warn_local_fallback(exc)
            return self._get_user_stats_local(user_id)


history_service = HistoryService()
