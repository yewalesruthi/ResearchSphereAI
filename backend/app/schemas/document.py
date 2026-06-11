from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: int
    workspace_id: int
    filename: str
    file_type: str
    page_count: int
    chunk_count: int
    file_size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentCompareRequest(BaseModel):
    workspace_id: int
    document_ids: List[int] = Field(min_length=2)


class DocumentCompareResponse(BaseModel):
    comparison_markdown: str
    document_names: List[str]
