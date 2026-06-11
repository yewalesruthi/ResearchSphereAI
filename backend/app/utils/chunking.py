from typing import List

import tiktoken


def get_tokenizer(model: str = "cl100k_base"):
    return tiktoken.get_encoding(model)


def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[str]:
    if not text.strip():
        return []

    enc = get_tokenizer()
    tokens = enc.encode(text)
    if len(tokens) <= chunk_size:
        return [text.strip()]

    chunks: List[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens).strip())
        if end >= len(tokens):
            break
        start = end - chunk_overlap

    return [c for c in chunks if c]
