"use client";

import { useEffect, useState } from "react";
import { FileText, Image, Mic, HardDrive, Plus, AlertTriangle } from "lucide-react";
import { AppLayout } from "@/components/layout/AppLayout";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import api, { checkBackendHealth, isNetworkError } from "@/lib/api";
import { useWorkspace } from "@/hooks/useWorkspace";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { formatBytes } from "@/lib/utils";
import type { DashboardStats } from "@/types";

export default function DashboardPage() {
  const { currentWorkspace, workspaces, setCurrentWorkspace } = useWorkspaceStore();
  const { createWorkspace, fetchWorkspaces } = useWorkspace();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [newWorkspaceName, setNewWorkspaceName] = useState("");
  const [creating, setCreating] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [backendDown, setBackendDown] = useState(false);
  const [statsError, setStatsError] = useState(false);

  useEffect(() => {
    checkBackendHealth().then((ok) => setBackendDown(!ok));
  }, []);

  useEffect(() => {
    if (!currentWorkspace || backendDown) return;

    const loadStats = async () => {
      try {
        const res = await api.get<DashboardStats>(`/dashboard/${currentWorkspace.id}`);
        setStats(res.data);
        setStatsError(false);
      } catch (err) {
        if (isNetworkError(err)) {
          setBackendDown(true);
        } else {
          setStatsError(true);
        }
      }
    };

    loadStats();
  }, [currentWorkspace, backendDown]);

  const handleCreateWorkspace = async () => {
    if (!newWorkspaceName.trim()) return;
    setCreating(true);
    try {
      await createWorkspace(newWorkspaceName.trim());
      await fetchWorkspaces();
      setNewWorkspaceName("");
      setDialogOpen(false);
    } catch (err) {
      if (isNetworkError(err)) setBackendDown(true);
    } finally {
      setCreating(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-8">
        {backendDown && (
          <div className="mb-6 flex items-center gap-3 rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            <AlertTriangle className="h-5 w-5 shrink-0" />
            <span>
              Backend not reachable — make sure the server is running on port 8000.
            </span>
          </div>
        )}

        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Overview of your research workspace</p>
          </div>
          <div className="flex items-center gap-3">
            {workspaces.length > 0 && (
              <select
                className="rounded-md border bg-background px-3 py-2 text-sm"
                value={currentWorkspace?.id ?? ""}
                onChange={(e) => {
                  const ws = workspaces.find((w) => w.id === Number(e.target.value));
                  if (ws) setCurrentWorkspace(ws);
                }}
              >
                {workspaces.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
              </select>
            )}
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4" />
                  New Workspace
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Workspace</DialogTitle>
                  <DialogDescription>
                    Give your research workspace a name to get started.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-2 py-2">
                  <Label htmlFor="workspace-name">Workspace name</Label>
                  <Input
                    id="workspace-name"
                    placeholder="e.g. ML Research"
                    value={newWorkspaceName}
                    onChange={(e) => setNewWorkspaceName(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleCreateWorkspace()}
                  />
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateWorkspace} disabled={creating || !newWorkspaceName.trim()}>
                    {creating ? "Creating..." : "Create"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {!currentWorkspace ? (
          <Card>
            <CardHeader>
              <CardTitle>Create Your First Workspace</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4 text-muted-foreground">
                Click <strong>+ New Workspace</strong> above to create your first research workspace.
              </p>
            </CardContent>
          </Card>
        ) : (
          <>
            <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <StatsCard title="Documents" value={stats?.document_count ?? 0} icon={FileText} />
              <StatsCard title="Images" value={stats?.image_count ?? 0} icon={Image} />
              <StatsCard title="Audio Files" value={stats?.audio_count ?? 0} icon={Mic} />
              <StatsCard
                title="Storage"
                value={formatBytes(stats?.storage_bytes ?? 0)}
                icon={HardDrive}
              />
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Recent Chat History</CardTitle>
              </CardHeader>
              <CardContent>
                {statsError ? (
                  <p className="text-muted-foreground">Could not load chat history.</p>
                ) : stats?.recent_messages && stats.recent_messages.length > 0 ? (
                  <div className="space-y-3">
                    {stats.recent_messages.map((msg, i) => (
                      <div key={i} className="rounded-md border p-3">
                        <span className="text-xs font-medium uppercase text-primary">{msg.role}</span>
                        <p className="mt-1 text-sm">{msg.content}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No chat history yet. Start a conversation!</p>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AppLayout>
  );
}
