"use client";

import { useCallback } from "react";
import { API_URL, getAuthHeaders } from "@/lib/api";
import { useChatStore } from "@/store/chatStore";
import type { SourceReference } from "@/types";

export function useChat(workspaceId: number | undefined) {
  const {
    messages,
    isStreaming,
    activeSources,
    addMessage,
    appendToLastMessage,
    setStreaming,
    setActiveSources,
    clearMessages,
  } = useChatStore();

  const sendMessage = useCallback(
    async (message: string) => {
      if (!workspaceId) return;

      addMessage({ role: "user", content: message });
      addMessage({ role: "assistant", content: "" });
      setStreaming(true);

      let sources: SourceReference[] = [];

      try {
        const response = await fetch(`${API_URL}/chat/stream`, {
          method: "POST",
          headers: getAuthHeaders(),
          credentials: "include",
          body: JSON.stringify({ workspace_id: workspaceId, message }),
        });

        if (!response.ok) throw new Error("Chat request failed");

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop() ?? "";

            for (const line of lines) {
              if (!line.startsWith("data: ")) continue;
              const data = JSON.parse(line.slice(6));
              if (data.type === "token") {
                appendToLastMessage(data.content);
              } else if (data.type === "done") {
                sources = data.sources || [];
                setActiveSources(sources);
              }
            }
          }
        }

        const lastMsg = useChatStore.getState().messages;
        const updated = [...lastMsg];
        if (updated.length > 0) {
          updated[updated.length - 1] = { ...updated[updated.length - 1], sources };
        }
        useChatStore.setState({ messages: updated });
      } catch {
        appendToLastMessage("\n\nError: Failed to get response. Check your API connection.");
      } finally {
        setStreaming(false);
      }

      return sources;
    },
    [workspaceId, addMessage, appendToLastMessage, setStreaming, setActiveSources]
  );

  return {
    messages,
    isStreaming,
    activeSources,
    sendMessage,
    clearMessages,
  };
}
