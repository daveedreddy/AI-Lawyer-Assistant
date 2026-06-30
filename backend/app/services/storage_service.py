"""
Supabase Storage service for uploaded legal documents.
Degrades gracefully when credentials are not yet configured.
"""

import logging
import mimetypes
from typing import Optional

from app.core.config import settings
from app.database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

BUCKET = settings.STORAGE_BUCKET_DOCUMENTS


class StorageService:

    def upload_file(self, path: str, content: bytes, content_type: Optional[str] = None) -> Optional[str]:
        """
        Upload raw bytes to Supabase Storage.
        Returns the storage path on success, None if Supabase is not configured.
        """
        sb = get_supabase()
        if not sb:
            logger.warning("Supabase not configured — file not uploaded to storage.")
            return None

        try:
            if not content_type:
                content_type, _ = mimetypes.guess_type(path)
                content_type = content_type or "application/octet-stream"

            sb.storage.from_(BUCKET).upload(
                path=path,
                file=content,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            logger.info("Uploaded file to storage: %s", path)
            return path
        except Exception as exc:
            logger.error("Storage upload failed for %s: %s", path, exc)
            return None

    def get_signed_url(self, path: str, expires_in: int = 3600) -> Optional[str]:
        """Returns a signed URL for a stored file, or None on failure."""
        sb = get_supabase()
        if not sb:
            return None
        try:
            result = sb.storage.from_(BUCKET).create_signed_url(path, expires_in)
            return result.get("signedURL") or result.get("signedUrl")
        except Exception as exc:
            logger.error("Signed URL generation failed for %s: %s", path, exc)
            return None

    def delete_file(self, path: str) -> bool:
        sb = get_supabase()
        if not sb:
            return False
        try:
            sb.storage.from_(BUCKET).remove([path])
            return True
        except Exception as exc:
            logger.error("Storage delete failed for %s: %s", path, exc)
            return False

    def save_document_record(
        self,
        user_id: Optional[str],
        session_id: Optional[str],
        file_name: str,
        file_size: str,
        detected_type: str,
        summary: str,
        storage_path: Optional[str],
    ) -> Optional[str]:
        """Insert a record into uploaded_documents table. Returns document id."""
        sb = get_supabase()
        if not sb:
            return None
        try:
            from uuid import uuid4
            from datetime import datetime, timezone
            record = {
                "id": str(uuid4()),
                "user_id": user_id,
                "session_id": session_id,
                "file_name": file_name,
                "file_size": file_size,
                "detected_type": detected_type,
                "summary": summary,
                "storage_path": storage_path,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            }
            result = sb.table("uploaded_documents").insert(record).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as exc:
            logger.error("Failed to save document record: %s", exc)
            return None


storage_service = StorageService()
