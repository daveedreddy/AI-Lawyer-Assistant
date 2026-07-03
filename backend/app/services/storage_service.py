import logging
import mimetypes
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.config import settings
from app.database.supabase_client import require_supabase

logger = logging.getLogger(__name__)

BUCKET = settings.STORAGE_BUCKET_DOCUMENTS


class StorageService:
    def upload_file(self, path: str, content: bytes, content_type: Optional[str] = None) -> str:
        sb = require_supabase()
        resolved_type = content_type
        if not resolved_type:
            resolved_type, _ = mimetypes.guess_type(path)
        resolved_type = resolved_type or "application/octet-stream"

        sb.storage.from_(BUCKET).upload(
            path=path,
            file=content,
            file_options={"content-type": resolved_type, "upsert": "true"},
        )
        logger.info("Uploaded file to Supabase storage: %s", path)
        return path

    def get_signed_url(self, path: str, expires_in: int = 3600) -> Optional[str]:
        sb = require_supabase()
        result = sb.storage.from_(BUCKET).create_signed_url(path, expires_in)
        return result.get("signedURL") or result.get("signedUrl")

    def delete_file(self, path: str) -> bool:
        sb = require_supabase()
        sb.storage.from_(BUCKET).remove([path])
        return True

    def save_document_record(
        self,
        user_id: str,
        session_id: Optional[str],
        file_name: str,
        file_size: str,
        detected_type: str,
        summary: str,
        storage_path: str,
    ) -> str:
        sb = require_supabase()
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
        return result.data[0]["id"] if result.data else record["id"]


storage_service = StorageService()
