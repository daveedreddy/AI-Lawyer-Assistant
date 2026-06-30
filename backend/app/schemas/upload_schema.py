from pydantic import BaseModel
from typing import List, Optional


class UploadResponse(BaseModel):
    fileName: str
    fileSize: str
    detectedType: str
    summary: str
    suggestedPrompts: List[str]
    storageUrl: Optional[str] = None
    documentId: Optional[str] = None