from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    workspace_id: int
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    chunk_id: str
    document: str
    page: Optional[int] = None
    text: str
    score: float
    vector_score: float
    bm25_score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]
