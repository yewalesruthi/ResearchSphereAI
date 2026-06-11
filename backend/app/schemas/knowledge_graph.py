from typing import List

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str


class KnowledgeGraphRequest(BaseModel):
    workspace_id: int


class KnowledgeGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
