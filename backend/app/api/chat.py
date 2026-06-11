import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.research_gap_agent import detect_research_gaps
from app.models.chat import ChatMessage
from app.models.database import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ResearchGapsRequest
from app.services.rag_pipeline import rag_query, rag_query_stream
from app.utils.deps import get_current_user, get_workspace_or_404

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)

    where = None
    if payload.document_ids:
        where = {"source_type": "document"}

    answer, sources, intent = rag_query(payload.workspace_id, payload.message, where=where)

    user_msg = ChatMessage(
        workspace_id=payload.workspace_id,
        user_id=current_user.id,
        role="user",
        content=payload.message,
        intent=intent,
    )
    assistant_msg = ChatMessage(
        workspace_id=payload.workspace_id,
        user_id=current_user.id,
        role="assistant",
        content=answer,
        sources_json=json.dumps([s.model_dump() for s in sources]),
        intent=intent,
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(answer=answer, sources=sources, intent=intent)


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)

    where = None
    if payload.document_ids:
        where = {"source_type": "document"}

    async def event_generator():
        full_answer = ""
        sources_data = []
        intent = "qa"
        async for event in rag_query_stream(payload.workspace_id, payload.message, where=where):
            if event["type"] == "token":
                full_answer += event["content"]
                yield f"data: {json.dumps(event)}\n\n"
            elif event["type"] == "done":
                sources_data = event.get("sources", [])
                intent = event.get("intent", "qa")
                yield f"data: {json.dumps(event)}\n\n"

        user_msg = ChatMessage(
            workspace_id=payload.workspace_id,
            user_id=current_user.id,
            role="user",
            content=payload.message,
            intent=intent,
        )
        assistant_msg = ChatMessage(
            workspace_id=payload.workspace_id,
            user_id=current_user.id,
            role="assistant",
            content=full_answer,
            sources_json=json.dumps(sources_data),
            intent=intent,
        )
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/research-gaps")
def research_gaps(
    payload: ResearchGapsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(db, payload.workspace_id, current_user.id)
    analysis = detect_research_gaps(payload.workspace_id)
    return {"analysis": analysis}
