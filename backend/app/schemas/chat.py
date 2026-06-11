from typing import List, Optional

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    document: str
    page: Optional[int] = None
    chunk_id: str


class ChatRequest(BaseModel):
    workspace_id: int
    message: str = Field(min_length=1)
    document_ids: Optional[List[int]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]
    intent: str


class ResearchGapsRequest(BaseModel):
    workspace_id: int
