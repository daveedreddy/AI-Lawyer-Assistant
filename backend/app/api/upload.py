import json
import logging
from pathlib import Path
import tempfile
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.core.auth import get_optional_user
from app.prompts.legal_prompt import UPLOAD_ANALYSIS_PROMPT
from app.schemas.upload_schema import UploadResponse
from app.services.document_parser import document_parser
from app.services.file_validator import file_validator
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

# Lazy import nvidia_service to avoid circular deps
def _get_llm():
    from app.services.nvidia_service import nvidia_service
    return nvidia_service



@router.post("/", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    user_id: Optional[str] = Depends(get_optional_user),
):
    try:
        extension = file_validator.validate(file)
        raw_bytes = await file.read()

        # Parse document text
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
            tmp.write(raw_bytes)
            tmp_path = tmp.name

        extracted_text = document_parser.parse(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)

        # LLM analysis with structured prompt
        llm = _get_llm()
        prompt = UPLOAD_ANALYSIS_PROMPT.format(
            document_text=extracted_text[:6000]  # token safety limit
        )
        raw_analysis = llm.generate_raw(prompt, max_tokens=600)

        # Parse JSON response from LLM
        detected_type = "Legal Document"
        summary = ""
        suggested_prompts = [
            "Summarize the legal obligations in this document.",
            "Identify any risky or unusual clauses.",
            "Explain this document in simple language.",
        ]

        try:
            # Strip markdown fences if model wraps in ```json ... ```
            clean = raw_analysis.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            analysis = json.loads(clean)
            detected_type = analysis.get("document_type", detected_type)
            summary = analysis.get("summary", "")
            llm_prompts = analysis.get("suggested_questions", [])
            if llm_prompts:
                suggested_prompts = llm_prompts[:3]
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning("Could not parse LLM document analysis JSON: %s", exc)
            summary = raw_analysis[:500] if raw_analysis else "Document processed successfully."

        # File size
        size_mb = round(len(raw_bytes) / (1024 * 1024), 2)
        file_size_str = f"{size_mb} MB"

        # Upload to Supabase Storage
        from uuid import uuid4
        storage_path = f"{user_id or 'anonymous'}/{uuid4()}{extension}"
        stored_path = storage_service.upload_file(
            path=storage_path,
            content=raw_bytes,
            content_type=file.content_type,
        )
        signed_url = storage_service.get_signed_url(stored_path) if stored_path else None

        # Save document record
        doc_id = storage_service.save_document_record(
            user_id=user_id,
            session_id=session_id,
            file_name=file.filename,
            file_size=file_size_str,
            detected_type=detected_type,
            summary=summary,
            storage_path=stored_path,
        )

        return UploadResponse(
            fileName=file.filename,
            fileSize=file_size_str,
            detectedType=detected_type,
            summary=summary,
            suggestedPrompts=suggested_prompts,
            storageUrl=signed_url,
            documentId=doc_id,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Upload processing failed")
        raise HTTPException(status_code=500, detail=str(exc))