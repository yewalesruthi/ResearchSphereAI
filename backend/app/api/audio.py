import json
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.audio import AudioFile
from app.models.database import get_db
from app.models.user import User
from app.schemas.audio import AudioQueryRequest, AudioQueryResponse, AudioResponse, TimestampReference
from app.services.audio_service import segments_to_json, transcribe_audio
from app.services.rag_pipeline import rag_query
from app.utils.chunking import chunk_text
from app.utils.config import get_settings
from app.utils.deps import get_current_user, get_workspace_or_404

router = APIRouter(prefix="/audio", tags=["audio"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a"}


def _upload_path(workspace_id: int, user_id: int, filename: str) -> Path:
    settings = get_settings()
    dest = Path(settings.upload_dir) / str(workspace_id) / str(user_id) / "audio"
    dest.mkdir(parents=True, exist_ok=True)
    return dest / filename


@router.get("/{workspace_id}", response_model=List[AudioResponse])
def list_audio(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, workspace_id, current_user.id)
    files = (
        db.query(AudioFile)
        .filter(AudioFile.workspace_id == workspace_id, AudioFile.user_id == current_user.id)
        .order_by(AudioFile.created_at.desc())
        .all()
    )
    return [AudioResponse.model_validate(f) for f in files]


@router.post("/upload", response_model=AudioResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    workspace_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, workspace_id, current_user.id)
    settings = get_settings()

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported audio type. Allowed: {ALLOWED_EXTENSIONS}")

    dest_path = _upload_path(workspace_id, current_user.id, file.filename)
    content = await file.read()
    dest_path.write_bytes(content)

    try:
        transcript, segments, duration = transcribe_audio(str(dest_path))
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Transcription failed: {exc}") from exc

    from app.vectorstore.chroma_client import add_chunks

    chunks = chunk_text(transcript, settings.chunk_size, settings.chunk_overlap) if transcript else []
    chunk_ids: List[str] = []
    if chunks:
        metadatas = [
            {
                "document": file.filename,
                "source_type": "audio",
                "workspace_id": workspace_id,
            }
            for _ in chunks
        ]
        chunk_ids = add_chunks(workspace_id, chunks, metadatas)

    audio = AudioFile(
        workspace_id=workspace_id,
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(dest_path),
        transcript=transcript,
        segments_json=segments_to_json(segments),
        chunk_count=len(chunk_ids),
        duration_seconds=duration,
        file_size_bytes=len(content),
    )
    db.add(audio)
    db.commit()
    db.refresh(audio)
    return AudioResponse.model_validate(audio)


@router.post("/query", response_model=AudioQueryResponse)
def query_audio(
    payload: AudioQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)

    where = {"source_type": "audio"}
    if payload.audio_id:
        audio = (
            db.query(AudioFile)
            .filter(
                AudioFile.id == payload.audio_id,
                AudioFile.workspace_id == payload.workspace_id,
                AudioFile.user_id == current_user.id,
            )
            .first()
        )
        if audio is None:
            raise HTTPException(status_code=404, detail="Audio file not found")

    answer, sources, _ = rag_query(payload.workspace_id, payload.query, where=where)

    timestamp_refs: List[TimestampReference] = []
    audio_files = (
        db.query(AudioFile)
        .filter(AudioFile.workspace_id == payload.workspace_id, AudioFile.user_id == current_user.id)
        .all()
    )
    for audio in audio_files:
        if audio.segments_json:
            segments = json.loads(audio.segments_json)
            for seg in segments:
                if any(word in seg["text"].lower() for word in payload.query.lower().split()[:3]):
                    timestamp_refs.append(
                        TimestampReference(
                            file=audio.filename,
                            start=seg["start_formatted"],
                            end=seg["end_formatted"],
                        )
                    )

    return AudioQueryResponse(answer=answer, timestamp_references=timestamp_refs[:5])
