import json
import logging
import re
from typing import List

from app.schemas.knowledge_graph import GraphEdge, GraphNode, KnowledgeGraphResponse
from app.services.llm_service import chat_completion
from app.vectorstore.chroma_client import get_all_chunks

logger = logging.getLogger(__name__)

GRAPH_PROMPT = """Extract entities and relationships from the research context.
Return ONLY valid JSON in this format:
{
  "nodes": [{"id": "1", "label": "Entity Name"}],
  "edges": [{"source": "1", "target": "2", "label": "relationship"}]
}
Extract key concepts, methods, datasets, and their relationships. Limit to 20 nodes."""


def generate_knowledge_graph(workspace_id: int) -> KnowledgeGraphResponse:
    all_data = get_all_chunks(workspace_id, limit=100)
    if not all_data.get("documents"):
        return KnowledgeGraphResponse(nodes=[], edges=[])

    combined_text = "\n\n".join(all_data["documents"][:30])
    context_chunks = [{"text": combined_text, "metadata": {}, "chunk_id": "combined"}]
    raw = chat_completion(GRAPH_PROMPT, context_chunks)

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON found")
        data = json.loads(match.group())
        nodes = [GraphNode(**n) for n in data.get("nodes", [])]
        edges = [GraphEdge(**e) for e in data.get("edges", [])]
        return KnowledgeGraphResponse(nodes=nodes, edges=edges)
    except Exception as exc:
        logger.error("Failed to parse knowledge graph: %s", exc)
        return KnowledgeGraphResponse(nodes=[], edges=[])
