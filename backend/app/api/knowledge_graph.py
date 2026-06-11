from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.knowledge_graph import KnowledgeGraphRequest, KnowledgeGraphResponse
from app.services.knowledge_graph_service import generate_knowledge_graph
from app.utils.deps import get_current_user, get_workspace_or_404

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


@router.post("/generate", response_model=KnowledgeGraphResponse)
def create_knowledge_graph(
    payload: KnowledgeGraphRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)
    return generate_knowledge_graph(payload.workspace_id)
