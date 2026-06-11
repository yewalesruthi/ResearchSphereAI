import logging
from typing import Dict, List

from rank_bm25 import BM25Okapi

from app.schemas.search import SearchResult
from app.vectorstore.chroma_client import get_all_chunks, query_chunks

logger = logging.getLogger(__name__)

VECTOR_WEIGHT = 0.6
BM25_WEIGHT = 0.4


def _tokenize(text: str) -> List[str]:
    return text.lower().split()


def _normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    if not scores:
        return {}
    values = list(scores.values())
    min_s, max_s = min(values), max(values)
    if max_s == min_s:
        return {k: 1.0 for k in scores}
    return {k: (v - min_s) / (max_s - min_s) for k, v in scores.items()}


def hybrid_search(workspace_id: int, query: str, top_k: int = 5) -> List[SearchResult]:
    vector_results = query_chunks(workspace_id, query, n_results=20)
    vector_scores: Dict[str, float] = {}
    chunk_data: Dict[str, Dict] = {}

    if vector_results.get("ids") and vector_results["ids"][0]:
        for i, chunk_id in enumerate(vector_results["ids"][0]):
            distance = vector_results["distances"][0][i]
            vector_scores[chunk_id] = max(0.0, 1.0 - distance)
            chunk_data[chunk_id] = {
                "text": vector_results["documents"][0][i],
                "metadata": vector_results["metadatas"][0][i],
            }

    all_chunks = get_all_chunks(workspace_id)
    bm25_scores: Dict[str, float] = {}
    if all_chunks.get("ids"):
        corpus = all_chunks["documents"]
        tokenized = [_tokenize(doc) for doc in corpus]
        bm25 = BM25Okapi(tokenized)
        scores = bm25.get_scores(_tokenize(query))
        for i, chunk_id in enumerate(all_chunks["ids"]):
            bm25_scores[chunk_id] = float(scores[i])
            if chunk_id not in chunk_data:
                chunk_data[chunk_id] = {
                    "text": all_chunks["documents"][i],
                    "metadata": all_chunks["metadatas"][i],
                }

    norm_vector = _normalize_scores(vector_scores)
    norm_bm25 = _normalize_scores(bm25_scores)

    all_ids = set(norm_vector.keys()) | set(norm_bm25.keys())
    combined: List[SearchResult] = []
    for chunk_id in all_ids:
        v_score = norm_vector.get(chunk_id, 0.0)
        b_score = norm_bm25.get(chunk_id, 0.0)
        final = VECTOR_WEIGHT * v_score + BM25_WEIGHT * b_score
        data = chunk_data.get(chunk_id, {})
        meta = data.get("metadata", {})
        page = meta.get("page")
        combined.append(
            SearchResult(
                chunk_id=chunk_id,
                document=meta.get("document", "unknown"),
                page=int(page) if page is not None else None,
                text=data.get("text", ""),
                score=final,
                vector_score=v_score,
                bm25_score=b_score,
            )
        )

    combined.sort(key=lambda x: x.score, reverse=True)
    return combined[:top_k]
