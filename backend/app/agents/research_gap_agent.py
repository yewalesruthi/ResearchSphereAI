from app.services.llm_service import chat_completion
from app.vectorstore.chroma_client import get_all_chunks

RESEARCH_GAP_PROMPT = """Analyze the provided research documents and identify:
1. Missing research areas
2. Common limitations across papers
3. Contradictions between documents
4. Suggested future work directions

Structure your response with clear headings for each section.
Base your analysis ONLY on the provided context."""


def detect_research_gaps(workspace_id: int) -> str:
    all_data = get_all_chunks(workspace_id, limit=200)
    if not all_data.get("documents"):
        return "No documents found in this workspace to analyze."

    combined = "\n\n".join(all_data["documents"][:50])
    context_chunks = [{"text": combined, "metadata": {}, "chunk_id": "workspace_context"}]
    return chat_completion(RESEARCH_GAP_PROMPT, context_chunks)
