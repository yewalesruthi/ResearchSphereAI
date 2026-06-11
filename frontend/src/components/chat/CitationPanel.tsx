"use client";

import { X, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SourceReference } from "@/types";

interface CitationPanelProps {
  sources: SourceReference[];
  selectedSource: SourceReference | null;
  onClose: () => void;
  onSelect: (source: SourceReference) => void;
}

export function CitationPanel({ sources, selectedSource, onClose, onSelect }: CitationPanelProps) {
  if (sources.length === 0) return null;

  return (
    <aside className="w-80 border-l bg-card p-4">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-semibold">Sources</h3>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>
      <div className="space-y-2">
        {sources.map((source, i) => (
          <Card
            key={`${source.chunk_id}-${i}`}
            className={`cursor-pointer transition-colors ${
              selectedSource?.chunk_id === source.chunk_id ? "border-primary" : ""
            }`}
            onClick={() => onSelect(source)}
          >
            <CardHeader className="p-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <FileText className="h-4 w-4" />
                {source.document}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-3 pt-0 text-xs text-muted-foreground">
              {source.page != null && <p>Page {source.page}</p>}
              <p className="truncate">Chunk: {source.chunk_id}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </aside>
  );
}
