from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RetrievedDocument(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float


class QueryResponse(BaseModel):
    query: str
    answer: str
    retrieved_documents: List[RetrievedDocument]
    confidence: float = Field(default=0.0)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    context: str = ""
    session_id: Optional[str] = None
