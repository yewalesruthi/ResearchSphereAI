import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.image import Image as ImageModel
from app.models.user import User
from app.schemas.image import ImageResponse, ImageUnderstandRequest, ImageUnderstandResponse
from app.services.llm_service import chat_completion, understand_image_with_vision, vision_available
from app.services.ocr_service import extract_image_metadata, extract_text_from_image
from app.utils.chunking import chunk_text
from app.utils.config import get_settings
from app.utils.deps import get_current_user, get_workspace_or_404
from app.vectorstore.chroma_client import add_chunks

router = APIRouter(prefix="/images", tags=["images"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tiff", "bmp"}


def _upload_path(workspace_id: int, user_id: int, filename: str) -> Path:
    settings = get_settings()
    dest = Path(settings.upload_dir) / str(workspace_id) / str(user_id) / "images"
    dest.mkdir(parents=True, exist_ok=True)
    return dest / filename


@router.get("/{workspace_id}", response_model=List[ImageResponse])
def list_images(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, workspace_id, current_user.id)
    images = (
        db.query(ImageModel)
        .filter(ImageModel.workspace_id == workspace_id, ImageModel.user_id == current_user.id)
        .order_by(ImageModel.created_at.desc())
        .all()
    )
    return [ImageResponse.model_validate(img) for img in images]


@router.post("/upload", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
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
        raise HTTPException(status_code=400, detail=f"Unsupported image type. Allowed: {ALLOWED_EXTENSIONS}")

    dest_path = _upload_path(workspace_id, current_user.id, file.filename)
    content = await file.read()
    dest_path.write_bytes(content)

    try:
        extracted_text = extract_text_from_image(str(dest_path))
    except Exception as exc:
        logger.warning("OCR failed: %s", exc)
        extracted_text = ""

    chunks = chunk_text(extracted_text, settings.chunk_size, settings.chunk_overlap) if extracted_text else []
    chunk_ids: List[str] = []
    if chunks:
        metadatas = [
            {
                "document": file.filename,
                "source_type": "ocr_image",
                "workspace_id": workspace_id,
            }
            for _ in chunks
        ]
        chunk_ids = add_chunks(workspace_id, chunks, metadatas)

    image = ImageModel(
        workspace_id=workspace_id,
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(dest_path),
        extracted_text=extracted_text or None,
        chunk_count=len(chunk_ids),
        file_size_bytes=len(content),
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return ImageResponse.model_validate(image)


@router.post("/understand", response_model=ImageUnderstandResponse)
def understand_image(
    payload: ImageUnderstandRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)
    image = (
        db.query(ImageModel)
        .filter(
            ImageModel.id == payload.image_id,
            ImageModel.workspace_id == payload.workspace_id,
            ImageModel.user_id == current_user.id,
        )
        .first()
    )
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    if vision_available():
        try:
            answer = understand_image_with_vision(image.file_path, payload.prompt)
            return ImageUnderstandResponse(answer=answer, method="groq_vision")
        except Exception as exc:
            logger.warning("Vision API failed, falling back to OCR: %s", exc)

    ocr_text = image.extracted_text or extract_text_from_image(image.file_path)
    metadata = extract_image_metadata(image.file_path)
    combined = f"OCR Text:\n{ocr_text}\n\nImage Metadata:\n{metadata}"
    context_chunks = [{"text": combined, "metadata": {"document": image.filename}, "chunk_id": str(image.id)}]
    answer = chat_completion(payload.prompt, context_chunks)
    return ImageUnderstandResponse(answer=answer, method="ocr_fallback")
