"use client";

import { useCallback, useEffect } from "react";
import api from "@/lib/api";
import { useWorkspaceStore } from "@/store/workspaceStore";
// useWorkspaceStore.getState used in fetchWorkspaces to avoid stale closure
import type { Workspace } from "@/types";

export function useWorkspace() {
  const {
    workspaces,
    currentWorkspace,
    setWorkspaces,
    setCurrentWorkspace,
    addWorkspace,
    removeWorkspace,
  } = useWorkspaceStore();

  const fetchWorkspaces = useCallback(async () => {
    try {
      const res = await api.get<Workspace[]>("/workspaces");
      setWorkspaces(res.data);
      const current = useWorkspaceStore.getState().currentWorkspace;
      if (!current && res.data.length > 0) {
        setCurrentWorkspace(res.data[0]);
      }
    } catch {
      // Caller surfaces backend-unreachable state (e.g. dashboard health banner)
    }
  }, [setWorkspaces, setCurrentWorkspace]);

  const createWorkspace = useCallback(
    async (name: string, description?: string) => {
      const res = await api.post<Workspace>("/workspaces", { name, description });
      addWorkspace(res.data);
      setCurrentWorkspace(res.data);
      return res.data;
    },
    [addWorkspace, setCurrentWorkspace]
  );

  const deleteWorkspace = useCallback(
    async (id: number) => {
      await api.delete(`/workspaces/${id}`);
      removeWorkspace(id);
    },
    [removeWorkspace]
  );

  return {
    workspaces,
    currentWorkspace,
    setCurrentWorkspace,
    fetchWorkspaces,
    createWorkspace,
    deleteWorkspace,
  };
}

export function useWorkspaceLoader(enabled: boolean) {
  const { fetchWorkspaces } = useWorkspace();

  useEffect(() => {
    if (enabled) fetchWorkspaces();
  }, [enabled, fetchWorkspaces]);
}
