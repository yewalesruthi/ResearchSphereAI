"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { KnowledgeGraph } from "@/types";

interface KnowledgeGraphViewProps {
  graph: KnowledgeGraph;
}

export function KnowledgeGraphView({ graph }: KnowledgeGraphViewProps) {
  const initialNodes: Node[] = useMemo(
    () =>
      graph.nodes.map((node, i) => ({
        id: node.id,
        data: { label: node.label },
        position: { x: (i % 5) * 200, y: Math.floor(i / 5) * 120 },
        style: {
          background: "#1e293b",
          color: "#f8fafc",
          border: "1px solid #334155",
          borderRadius: "8px",
          padding: "10px",
          fontSize: "12px",
        },
      })),
    [graph.nodes]
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      graph.edges.map((edge, i) => ({
        id: `e-${i}`,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        animated: true,
        style: { stroke: "#6366f1" },
      })),
    [graph.edges]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const onInit = useCallback(() => {}, []);

  if (graph.nodes.length === 0) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg border bg-muted/50">
        <p className="text-muted-foreground">No graph data. Upload documents and generate a graph.</p>
      </div>
    );
  }

  return (
    <div className="h-[600px] rounded-lg border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onInit={onInit}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
