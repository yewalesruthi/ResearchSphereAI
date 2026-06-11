from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ImageResponse(BaseModel):
    id: int
    workspace_id: int
    filename: str
    extracted_text: Optional[str]
    chunk_count: int
    file_size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ImageUnderstandRequest(BaseModel):
    image_id: int
    workspace_id: int
    prompt: str = Field(default="Explain this image", min_length=1)


class ImageUnderstandResponse(BaseModel):
    answer: str
    method: str
