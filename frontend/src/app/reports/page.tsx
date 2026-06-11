"use client";

import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import api from "@/lib/api";
import { useWorkspaceStore } from "@/store/workspaceStore";

const REPORT_TYPES = [
  { value: "study_notes", label: "Study Notes" },
  { value: "research_summary", label: "Research Summary" },
  { value: "executive_summary", label: "Executive Summary" },
  { value: "literature_review", label: "Literature Review" },
] as const;

export default function ReportsPage() {
  const currentWorkspace = useWorkspaceStore((s) => s.currentWorkspace);
  const [reportType, setReportType] = useState<string>("research_summary");
  const [format, setFormat] = useState<"pdf" | "docx">("pdf");
  const [literatureContent, setLiteratureContent] = useState("");
  const [loading, setLoading] = useState(false);

  const generateReport = async () => {
    if (!currentWorkspace) return;
    setLoading(true);
    try {
      const res = await api.post(
        "/reports/generate",
        {
          workspace_id: currentWorkspace.id,
          report_type: reportType,
          export_format: format,
        },
        { responseType: "blob" }
      );
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.download = `report.${format}`;
      link.click();
      window.URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  };

  const generateLiteratureReview = async () => {
    if (!currentWorkspace) return;
    setLoading(true);
    try {
      const docsRes = await api.get(`/documents/${currentWorkspace.id}`);
      const docIds = docsRes.data.map((d: { id: number }) => d.id);
      if (docIds.length === 0) {
        setLiteratureContent("No documents in workspace.");
        return;
      }
      const res = await api.post<{ content: string }>("/reports/literature-review", {
        workspace_id: currentWorkspace.id,
        document_ids: docIds,
      });
      setLiteratureContent(res.data.content);
    } finally {
      setLoading(false);
    }
  };

  const detectGaps = async () => {
    if (!currentWorkspace) return;
    setLoading(true);
    try {
      const res = await api.post<{ analysis: string }>("/chat/research-gaps", {
        workspace_id: currentWorkspace.id,
      });
      setLiteratureContent(res.data.analysis);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-8">
        <h1 className="mb-2 text-3xl font-bold">Reports</h1>
        <p className="mb-8 text-muted-foreground">Generate and export research reports</p>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Export Report</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <select
                className="w-full rounded-md border bg-background px-3 py-2"
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
              >
                {REPORT_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
              <select
                className="w-full rounded-md border bg-background px-3 py-2"
                value={format}
                onChange={(e) => setFormat(e.target.value as "pdf" | "docx")}
              >
                <option value="pdf">PDF</option>
                <option value="docx">DOCX</option>
              </select>
              <Button onClick={generateReport} disabled={loading || !currentWorkspace} className="w-full">
                Download Report
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>AI Analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button onClick={generateLiteratureReview} disabled={loading} variant="outline" className="w-full">
                Generate Literature Review
              </Button>
              <Button onClick={detectGaps} disabled={loading} variant="outline" className="w-full">
                Detect Research Gaps
              </Button>
            </CardContent>
          </Card>
        </div>

        {literatureContent && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Generated Content</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap text-sm">{literatureContent}</pre>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
