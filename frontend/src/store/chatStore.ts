import { create } from "zustand";
import type { ChatMessage, SourceReference } from "@/types";

interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
  activeSources: SourceReference[];
  addMessage: (message: ChatMessage) => void;
  appendToLastMessage: (content: string) => void;
  setStreaming: (streaming: boolean) => void;
  setActiveSources: (sources: SourceReference[]) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  activeSources: [],
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  appendToLastMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      const last = messages[messages.length - 1];
      if (last && last.role === "assistant") {
        messages[messages.length - 1] = { ...last, content: last.content + content };
      }
      return { messages };
    }),
  setStreaming: (streaming) => set({ isStreaming: streaming }),
  setActiveSources: (sources) => set({ activeSources: sources }),
  clearMessages: () => set({ messages: [], activeSources: [] }),
}));
