"use client";

import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import api from "@/lib/api";
import { useWorkspaceStore } from "@/store/workspaceStore";
import type { SearchResult } from "@/types";

export default function SearchPage() {
  const currentWorkspace = useWorkspaceStore((s) => s.currentWorkspace);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentWorkspace || !query.trim()) return;
    setLoading(true);
    try {
      const res = await api.post<{ results: SearchResult[] }>("/search", {
        workspace_id: currentWorkspace.id,
        query,
        top_k: 5,
      });
      setResults(res.data.results);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-8">
        <h1 className="mb-2 text-3xl font-bold">Hybrid Search</h1>
        <p className="mb-8 text-muted-foreground">
          Vector + BM25 search across your workspace (0.6 vector / 0.4 keyword)
        </p>
        <form onSubmit={handleSearch} className="mb-8 flex gap-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your documents..."
            className="max-w-xl"
          />
          <Button type="submit" disabled={loading || !currentWorkspace}>
            {loading ? "Searching..." : "Search"}
          </Button>
        </form>
        <div className="space-y-4">
          {results.map((result) => (
            <Card key={result.chunk_id}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">
                  {result.document}
                  {result.page != null && ` — Page ${result.page}`}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">{result.text}</p>
                <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                  <span>Score: {result.score.toFixed(3)}</span>
                  <span>Vector: {result.vector_score.toFixed(3)}</span>
                  <span>BM25: {result.bm25_score.toFixed(3)}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
