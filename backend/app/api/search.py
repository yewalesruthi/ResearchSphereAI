from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.hybrid_search import hybrid_search
from app.utils.deps import get_current_user, get_workspace_or_404

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)
    results = hybrid_search(payload.workspace_id, payload.query, top_k=payload.top_k)
    return SearchResponse(results=results)
