"use client";

import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useSettingsStore, GROQ_MODELS } from "@/store/settingsStore";
import { useWorkspace } from "@/hooks/useWorkspace";

export default function SettingsPage() {
  const { llmModel, embeddingModel, groqApiKey, setLlmModel, setEmbeddingModel, setGroqApiKey } =
    useSettingsStore();
  const { workspaces, deleteWorkspace } = useWorkspace();
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <AppLayout>
      <div className="max-w-2xl p-8">
        <h1 className="mb-2 text-3xl font-bold">Settings</h1>
        <p className="mb-8 text-muted-foreground">Configure models and manage workspaces</p>

        <Accordion type="multiple" className="w-full">
          <AccordionItem value="llm">
            <AccordionTrigger>LLM Configuration</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>LLM Model</Label>
                  <select
                    className="w-full rounded-md border bg-background px-3 py-2"
                    value={llmModel}
                    onChange={(e) => setLlmModel(e.target.value)}
                  >
                    {GROQ_MODELS.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>
                <p className="text-sm text-muted-foreground">
                  Groq model used for chat and report generation (stored locally).
                </p>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="embedding">
            <AccordionTrigger>Embedding Settings</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-2">
                <Label>Embedding Model</Label>
                <Input value={embeddingModel} onChange={(e) => setEmbeddingModel(e.target.value)} />
                <p className="text-sm text-muted-foreground">
                  Reference only — the active embedding model is configured on the backend.
                </p>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="workspaces">
            <AccordionTrigger>Workspace Management</AccordionTrigger>
            <AccordionContent>
              {workspaces.length === 0 ? (
                <p className="text-muted-foreground">No workspaces</p>
              ) : (
                <div className="space-y-2">
                  {workspaces.map((ws) => (
                    <div key={ws.id} className="flex items-center justify-between rounded-md border p-3">
                      <span>{ws.name}</span>
                      <Button variant="destructive" size="sm" onClick={() => deleteWorkspace(ws.id)}>
                        Delete
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="api-keys">
            <AccordionTrigger>API Keys</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Groq API Key (reference only — set on backend)</Label>
                  <Input
                    type="password"
                    value={groqApiKey}
                    onChange={(e) => setGroqApiKey(e.target.value)}
                    placeholder="gsk_..."
                  />
                </div>
                <Button onClick={handleSave}>{saved ? "Saved!" : "Save Settings"}</Button>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </AppLayout>
  );
}
