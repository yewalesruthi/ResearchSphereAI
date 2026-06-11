import base64
import logging
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional

from groq import Groq

from app.utils.config import get_settings

logger = logging.getLogger(__name__)

CITATION_SYSTEM_PROMPT = """You are ResearchSphere AI, a research assistant.
Answer ONLY using the provided context. If the answer is not supported by the context, say "Not found in documents."
Always cite sources inline using [document_name, page N] format when page numbers are available.
Be precise, academic, and concise."""

_client: Optional[Groq] = None


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        settings = get_settings()
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def build_context_block(chunks: List[Dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        doc = meta.get("document", "unknown")
        page = meta.get("page")
        chunk_id = chunk.get("chunk_id", "")
        page_str = f", page {page}" if page else ""
        parts.append(f"[Source {i}] document={doc}{page_str}, chunk_id={chunk_id}\n{chunk['text']}")
    return "\n\n".join(parts)


def chat_completion(
    user_message: str,
    context_chunks: List[Dict],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    settings = get_settings()
    client = get_groq_client()
    context = build_context_block(context_chunks)
    messages = [
        {"role": "system", "content": system_prompt or CITATION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {user_message}",
        },
    ]
    try:
        response = client.chat.completions.create(
            model=model or settings.llm_model,
            messages=messages,
            temperature=0.2,
            max_tokens=4096,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        logger.error("Groq chat completion failed: %s", exc)
        raise


async def chat_completion_stream(
    user_message: str,
    context_chunks: List[Dict],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    settings = get_settings()
    client = get_groq_client()
    context = build_context_block(context_chunks)
    messages = [
        {"role": "system", "content": system_prompt or CITATION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {user_message}",
        },
    ]
    stream = client.chat.completions.create(
        model=model or settings.llm_model,
        messages=messages,
        temperature=0.2,
        max_tokens=4096,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def vision_available() -> bool:
    settings = get_settings()
    if not settings.groq_api_key:
        return False
    try:
        client = get_groq_client()
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        return settings.vision_model in model_ids
    except Exception as exc:
        logger.warning("Vision model check failed: %s", exc)
        return False


def understand_image_with_vision(image_path: str, prompt: str) -> str:
    settings = get_settings()
    client = get_groq_client()
    image_bytes = Path(image_path).read_bytes()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    ext = Path(image_path).suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext

    response = client.chat.completions.create(
        model=settings.vision_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{mime};base64,{b64}"},
                    },
                ],
            }
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    return response.choices[0].message.content or ""
