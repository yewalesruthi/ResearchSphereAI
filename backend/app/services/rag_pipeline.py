import logging
from typing import Dict, List, Optional, Tuple

from sentence_transformers import CrossEncoder

from app.schemas.chat import SourceReference
from app.services.llm_service import CITATION_SYSTEM_PROMPT, chat_completion, chat_completion_stream
from app.vectorstore.chroma_client import query_chunks, verify_chunk_ids

logger = logging.getLogger(__name__)

_cross_encoder: Optional[CrossEncoder] = None
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        logger.info("Loading cross-encoder: %s", RERANK_MODEL)
        _cross_encoder = CrossEncoder(RERANK_MODEL)
    return _cross_encoder


def detect_intent(message: str) -> str:
    lower = message.lower()
    if any(w in lower for w in ["summarize", "summary", "overview"]):
        return "summarization"
    if any(w in lower for w in ["compare", "comparison", "versus", " vs "]):
        return "comparison"
    return "qa"


def _parse_chroma_results(results: Dict) -> List[Dict]:
    chunks: List[Dict] = []
    if not results.get("ids") or not results["ids"][0]:
        return chunks

    for i, chunk_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
        distance = results["distances"][0][i] if results.get("distances") else 1.0
        text = results["documents"][0][i] if results.get("documents") else ""
        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "metadata": metadata,
                "vector_score": max(0.0, 1.0 - distance),
            }
        )
    return chunks


def rerank_chunks(query: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
    if not chunks:
        return []
    if len(chunks) <= top_k:
        return chunks

    encoder = get_cross_encoder()
    pairs = [[query, c["text"]] for c in chunks]
    scores = encoder.predict(pairs)
    for i, score in enumerate(scores):
        chunks[i]["rerank_score"] = float(score)
    chunks.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
    return chunks[:top_k]


def retrieve_and_rerank(
    workspace_id: int,
    query: str,
    n_retrieve: int = 10,
    n_select: int = 5,
    where: Optional[Dict] = None,
) -> List[Dict]:
    results = query_chunks(workspace_id, query, n_results=n_retrieve, where=where)
    chunks = _parse_chroma_results(results)
    verified_ids = verify_chunk_ids(workspace_id, [c["chunk_id"] for c in chunks])
    chunks = [c for c in chunks if c["chunk_id"] in verified_ids]
    return rerank_chunks(query, chunks, top_k=n_select)


def build_sources(chunks: List[Dict]) -> List[SourceReference]:
    sources: List[SourceReference] = []
    seen = set()
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        doc = meta.get("document", "unknown")
        page = meta.get("page")
        chunk_id = chunk["chunk_id"]
        key = (doc, page, chunk_id)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            SourceReference(
                document=doc,
                page=int(page) if page is not None else None,
                chunk_id=chunk_id,
            )
        )
    return sources


def get_prompt_for_intent(intent: str) -> str:
    base = CITATION_SYSTEM_PROMPT
    extras = {
        "summarization": "\nProvide a structured summary covering key themes, methods, and findings.",
        "comparison": "\nCompare and contrast the sources, highlighting similarities and differences.",
        "qa": "\nAnswer the specific question directly using evidence from the sources.",
    }
    return base + extras.get(intent, extras["qa"])


async def rag_query_stream(
    workspace_id: int,
    message: str,
    where: Optional[Dict] = None,
):
    intent = detect_intent(message)
    chunks = retrieve_and_rerank(workspace_id, message, where=where)
    sources = build_sources(chunks)
    system_prompt = get_prompt_for_intent(intent)

    if not chunks:
        yield {"type": "token", "content": "Not found in documents."}
        yield {"type": "done", "sources": [s.model_dump() for s in sources], "intent": intent}
        return

    full_answer = ""
    async for token in chat_completion_stream(message, chunks, system_prompt=system_prompt):
        full_answer += token
        yield {"type": "token", "content": token}

    yield {"type": "done", "sources": [s.model_dump() for s in sources], "intent": intent}


def rag_query(
    workspace_id: int,
    message: str,
    where: Optional[Dict] = None,
) -> Tuple[str, List[SourceReference], str]:
    intent = detect_intent(message)
    chunks = retrieve_and_rerank(workspace_id, message, where=where)
    sources = build_sources(chunks)
    system_prompt = get_prompt_for_intent(intent)

    if not chunks:
        return "Not found in documents.", sources, intent

    answer = chat_completion(message, chunks, system_prompt=system_prompt)
    return answer, sources, intent
