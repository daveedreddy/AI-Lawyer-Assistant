from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    fileName: str
    fileSize: str
    detectedType: str
    summary: str
    suggestedPrompts: List[str]
    storageUrl: Optional[str] = None
    documentId: Optional[str] = None
    userMessage: Optional[Dict[str, Any]] = None
    assistantMessage: Optional[Dict[str, Any]] = None
