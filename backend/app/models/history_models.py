from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: str  # "user" | "ai"
    content: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: Optional[float] = None
    timestamp: datetime


class ChatSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    title: str
    messages: List[ChatMessage] = Field(default_factory=list)
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UploadedDocument(BaseModel):
    id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    file_name: str
    file_size: str
    detected_type: str
    summary: str
    storage_url: Optional[str] = None
    uploaded_at: datetime