import logging
import uuid
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.utils.config import get_settings

logger = logging.getLogger(__name__)

_embedding_model: Optional[SentenceTransformer] = None
_chroma_client: Optional[chromadb.PersistentClient] = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        settings = get_settings()
        logger.info("Loading embedding model: %s", settings.embedding_model)
        _embedding_model = SentenceTransformer(settings.embedding_model)
    return _embedding_model


def get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        settings = get_settings()
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


def workspace_collection_name(workspace_id: int) -> str:
    return f"workspace_{workspace_id}"


def get_or_create_collection(workspace_id: int):
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=workspace_collection_name(workspace_id),
        metadata={"hnsw:space": "cosine"},
    )


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def add_chunks(
    workspace_id: int,
    texts: List[str],
    metadatas: List[Dict[str, Any]],
    ids: Optional[List[str]] = None,
) -> List[str]:
    if not texts:
        return []

    collection = get_or_create_collection(workspace_id)
    chunk_ids = ids or [str(uuid.uuid4()) for _ in texts]
    embeddings = embed_texts(texts)
    collection.add(ids=chunk_ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    return chunk_ids


def query_chunks(
    workspace_id: int,
    query: str,
    n_results: int = 10,
    where: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    collection = get_or_create_collection(workspace_id)
    query_embedding = embed_texts([query])[0]
    kwargs: Dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where
    return collection.query(**kwargs)


def verify_chunk_ids(workspace_id: int, chunk_ids: List[str]) -> List[str]:
    if not chunk_ids:
        return []
    collection = get_or_create_collection(workspace_id)
    result = collection.get(ids=chunk_ids, include=["documents"])
    return result.get("ids", [])


def get_all_chunks(workspace_id: int, limit: int = 500) -> Dict[str, Any]:
    collection = get_or_create_collection(workspace_id)
    return collection.get(limit=limit, include=["documents", "metadatas"])


def delete_workspace_collection(workspace_id: int) -> None:
    client = get_chroma_client()
    name = workspace_collection_name(workspace_id)
    try:
        client.delete_collection(name)
    except Exception:
        logger.warning("Collection %s not found for deletion", name)
