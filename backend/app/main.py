import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, audio, chat, dashboard, documents, images, knowledge_graph, reports, search, workspaces
from app.models.database import init_db
from app.utils.config import get_settings
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    init_db()
    logger.info("ResearchSphere AI backend started")
    yield
    logger.info("ResearchSphere AI backend shutting down")


app = FastAPI(
    title="ResearchSphere AI",
    description="Multimodal AI research assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(documents.router)
app.include_router(images.router)
app.include_router(audio.router)
app.include_router(chat.router)
app.include_router(search.router)
app.include_router(reports.router)
app.include_router(knowledge_graph.router)
app.include_router(dashboard.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "researchsphere-ai"}
