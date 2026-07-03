import json
import logging
from pathlib import Path
import tempfile
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.auth import get_current_user
from app.prompts.legal_prompt import UPLOAD_ANALYSIS_PROMPT
from app.schemas.upload_schema import UploadResponse
from app.services.document_parser import document_parser
from app.services.file_validator import file_validator
from app.services.history_service import history_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def _get_llm():
    from app.services.nvidia_service import nvidia_service

    return nvidia_service


def _parse_analysis(raw_analysis: str) -> tuple[str, str, list[str]]:
    detected_type = "Legal Document"
    suggested_prompts = [
        "Summarize the legal obligations in this document.",
        "Identify any risky or unusual clauses.",
        "Explain this document in simple language.",
    ]

    clean = raw_analysis.strip()
    if clean.startswith("```"):
        clean = clean.strip("`").strip()
        if clean.startswith("json"):
            clean = clean[4:].strip()

    analysis = json.loads(clean)
    detected_type = analysis.get("document_type") or detected_type
    summary = analysis.get("summary") or "Document processed successfully."
    llm_prompts = analysis.get("suggested_questions") or []
    if isinstance(llm_prompts, list) and llm_prompts:
        suggested_prompts = [str(prompt) for prompt in llm_prompts[:3]]

    return detected_type, summary, suggested_prompts


@router.post("/", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    user_id: str = Depends(get_current_user),
):
    tmp_path = None
    try:
        if session_id and not history_service.get_session(session_id, user_id):
            raise HTTPException(status_code=404, detail="Session not found.")

        extension = file_validator.validate(file)
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if len(raw_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File size exceeds the 10 MB limit.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
            tmp.write(raw_bytes)
            tmp_path = tmp.name

        extracted_text = document_parser.parse(tmp_path)
        if not extracted_text.strip():
            raise HTTPException(status_code=422, detail="No text could be extracted from this file.")

        prompt = UPLOAD_ANALYSIS_PROMPT.format(document_text=extracted_text[:6000])
        raw_analysis = _get_llm().generate_raw(prompt, max_tokens=600)

        try:
            detected_type, summary, suggested_prompts = _parse_analysis(raw_analysis)
        except Exception as exc:
            logger.warning("Could not parse LLM document analysis JSON: %s", exc)
            detected_type = "Legal Document"
            summary = raw_analysis[:800].strip() or "Document processed successfully."
            suggested_prompts = [
                "Summarize the legal obligations in this document.",
                "Identify any risky or unusual clauses.",
                "Explain this document in simple language.",
            ]

        size_mb = round(len(raw_bytes) / (1024 * 1024), 2)
        file_size_str = f"{size_mb} MB"
        safe_filename = file.filename or f"document{extension}"
        storage_path = f"{user_id}/{uuid4()}{extension}"
        stored_path = storage_service.upload_file(
            path=storage_path,
            content=raw_bytes,
            content_type=file.content_type,
        )
        signed_url = storage_service.get_signed_url(stored_path)
        doc_id = storage_service.save_document_record(
            user_id=user_id,
            session_id=session_id,
            file_name=safe_filename,
            file_size=file_size_str,
            detected_type=detected_type,
            summary=summary,
            storage_path=stored_path,
        )

        user_message = None
        assistant_message = None
        if session_id:
            user_message = history_service.add_message(
                session_id=session_id,
                role="user",
                content=f"Please analyze this document: {safe_filename}",
                user_id=user_id,
            )
            assistant_message = history_service.add_message(
                session_id=session_id,
                role="ai",
                content=(
                    f"**Document Uploaded**: `{safe_filename}` ({file_size_str})\n"
                    f"**Detected Type**: *{detected_type}*\n\n"
                    f"### Summary:\n{summary}"
                ),
                user_id=user_id,
            )

        return UploadResponse(
            fileName=safe_filename,
            fileSize=file_size_str,
            detectedType=detected_type,
            summary=summary,
            suggestedPrompts=suggested_prompts,
            storageUrl=signed_url,
            documentId=doc_id,
            userMessage=user_message.model_dump(mode="json") if user_message else None,
            assistantMessage=assistant_message.model_dump(mode="json") if assistant_message else None,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Upload processing failed")
        raise HTTPException(status_code=500, detail="Upload processing failed.") from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
