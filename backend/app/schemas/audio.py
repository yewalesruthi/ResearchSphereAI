from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AudioResponse(BaseModel):
    id: int
    workspace_id: int
    filename: str
    duration_seconds: float
    chunk_count: int
    file_size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TimestampReference(BaseModel):
    file: str
    start: str
    end: str


class AudioQueryRequest(BaseModel):
    workspace_id: int
    query: str = Field(min_length=1)
    audio_id: Optional[int] = None


class AudioQueryResponse(BaseModel):
    answer: str
    timestamp_references: List[TimestampReference]
