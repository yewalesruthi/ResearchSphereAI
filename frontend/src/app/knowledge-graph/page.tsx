"use client";

import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { KnowledgeGraphView } from "@/components/knowledge-graph/KnowledgeGraphView";
import { Button } from "@/components/ui/button";
import api from "@/lib/api";
import { useWorkspaceStore } from "@/store/workspaceStore";
import type { KnowledgeGraph } from "@/types";

export default function KnowledgeGraphPage() {
  const currentWorkspace = useWorkspaceStore((s) => s.currentWorkspace);
  const [graph, setGraph] = useState<KnowledgeGraph>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(false);

  const generateGraph = async () => {
    if (!currentWorkspace) return;
    setLoading(true);
    try {
      const res = await api.post<KnowledgeGraph>("/knowledge-graph/generate", {
        workspace_id: currentWorkspace.id,
      });
      setGraph(res.data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Knowledge Graph</h1>
            <p className="text-muted-foreground">Visualize entities and relationships from your documents</p>
          </div>
          <Button onClick={generateGraph} disabled={loading || !currentWorkspace}>
            {loading ? "Generating..." : "Generate Graph"}
          </Button>
        </div>
        <KnowledgeGraphView graph={graph} />
      </div>
    </AppLayout>
  );
}
