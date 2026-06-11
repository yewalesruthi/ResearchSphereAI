import json
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCompareRequest, DocumentCompareResponse, DocumentResponse
from app.services.document_parser import parse_document
from app.services.llm_service import chat_completion
from app.utils.chunking import chunk_text
from app.utils.config import get_settings
from app.utils.deps import get_current_user, get_workspace_or_404
from app.vectorstore.chroma_client import add_chunks

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"pdf", "docx", "pptx", "txt"}


def _upload_path(workspace_id: int, user_id: int, filename: str) -> Path:
    settings = get_settings()
    dest = Path(settings.upload_dir) / str(workspace_id) / str(user_id) / "documents"
    dest.mkdir(parents=True, exist_ok=True)
    return dest / filename


@router.get("/{workspace_id}", response_model=List[DocumentResponse])
def list_documents(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, workspace_id, current_user.id)
    docs = (
        db.query(Document)
        .filter(Document.workspace_id == workspace_id, Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [DocumentResponse.model_validate(d) for d in docs]


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
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
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {ALLOWED_TYPES}")

    dest_path = _upload_path(workspace_id, current_user.id, file.filename)
    content = await file.read()
    dest_path.write_bytes(content)

    try:
        text, page_count = parse_document(str(dest_path), ext)
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {exc}") from exc

    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    metadatas = [
        {
            "document": file.filename,
            "page": 1,
            "source_type": "document",
            "workspace_id": workspace_id,
        }
        for _ in chunks
    ]
    chunk_ids = add_chunks(workspace_id, chunks, metadatas)

    doc = Document(
        workspace_id=workspace_id,
        user_id=current_user.id,
        filename=file.filename,
        file_type=ext,
        file_path=str(dest_path),
        page_count=page_count,
        chunk_count=len(chunk_ids),
        file_size_bytes=len(content),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return DocumentResponse.model_validate(doc)


@router.post("/compare", response_model=DocumentCompareResponse)
def compare_documents(
    payload: DocumentCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)
    docs = (
        db.query(Document)
        .filter(
            Document.id.in_(payload.document_ids),
            Document.workspace_id == payload.workspace_id,
            Document.user_id == current_user.id,
        )
        .all()
    )
    if len(docs) < 2:
        raise HTTPException(status_code=400, detail="At least 2 valid documents required")

    names = [d.filename for d in docs]
    prompt = (
        f"Compare these documents: {', '.join(names)}. "
        "Generate a Markdown comparison table with rows: Method, Dataset, Results, Conclusion. "
        "One column per document."
    )
    context_chunks = []
    for doc in docs:
        try:
            text, _ = parse_document(doc.file_path, doc.file_type)
            context_chunks.append(
                {"text": text[:8000], "metadata": {"document": doc.filename}, "chunk_id": str(doc.id)}
            )
        except Exception as exc:
            logger.warning("Could not parse %s: %s", doc.filename, exc)

    comparison = chat_completion(prompt, context_chunks)
    return DocumentCompareResponse(comparison_markdown=comparison, document_names=names)
