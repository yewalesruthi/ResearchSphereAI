import json
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.audio import AudioFile
from app.models.chat import ChatMessage
from app.models.database import get_db
from app.models.document import Document
from app.models.image import Image as ImageModel
from app.models.user import User
from app.utils.deps import get_current_user, get_workspace_or_404

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    document_count: int
    image_count: int
    audio_count: int
    storage_bytes: int
    recent_messages: List[dict]


@router.get("/{workspace_id}", response_model=DashboardStats)
def get_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, workspace_id, current_user.id)

    docs = (
        db.query(Document)
        .filter(Document.workspace_id == workspace_id, Document.user_id == current_user.id)
        .all()
    )
    images = (
        db.query(ImageModel)
        .filter(ImageModel.workspace_id == workspace_id, ImageModel.user_id == current_user.id)
        .all()
    )
    audio_files = (
        db.query(AudioFile)
        .filter(AudioFile.workspace_id == workspace_id, AudioFile.user_id == current_user.id)
        .all()
    )
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.workspace_id == workspace_id, ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
        .all()
    )

    storage = sum(d.file_size_bytes for d in docs)
    storage += sum(i.file_size_bytes for i in images)
    storage += sum(a.file_size_bytes for a in audio_files)

    recent = []
    for msg in reversed(messages):
        sources = None
        if msg.sources_json:
            try:
                sources = json.loads(msg.sources_json)
            except json.JSONDecodeError:
                sources = None
        recent.append(
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content[:200],
                "intent": msg.intent,
                "sources": sources,
                "created_at": msg.created_at.isoformat(),
            }
        )

    return DashboardStats(
        document_count=len(docs),
        image_count=len(images),
        audio_count=len(audio_files),
        storage_bytes=storage,
        recent_messages=recent,
    )
