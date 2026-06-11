from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.agents.literature_review_agent import run_literature_review
from app.models.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.report import LiteratureReviewRequest, ReportGenerateRequest
from app.services.report_generator import export_to_docx, export_to_pdf, generate_report_content
from app.utils.deps import get_current_user, get_workspace_or_404

router = APIRouter(prefix="/reports", tags=["reports"])


def _get_document_names(db: Session, workspace_id: int, user_id: int, doc_ids: List[int] | None) -> List[str]:
    query = db.query(Document).filter(Document.workspace_id == workspace_id, Document.user_id == user_id)
    if doc_ids:
        query = query.filter(Document.id.in_(doc_ids))
    return [d.filename for d in query.all()]


@router.post("/generate")
def generate_report(
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)
    names = _get_document_names(db, payload.workspace_id, current_user.id, payload.document_ids)
    content = generate_report_content(payload.workspace_id, payload.report_type, names)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if payload.export_format == "docx":
        path = export_to_docx(content, f"report_{timestamp}.docx")
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        path = export_to_pdf(content, f"report_{timestamp}.pdf")
        media = "application/pdf"

    return FileResponse(path, media_type=media, filename=path.split("/")[-1].split("\\")[-1])


@router.post("/literature-review")
def literature_review(
    payload: LiteratureReviewRequest,
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
    if not docs:
        raise HTTPException(status_code=400, detail="No valid documents found")

    names = [d.filename for d in docs]
    content = run_literature_review(payload.workspace_id, names)
    return {"content": content, "document_names": names}
