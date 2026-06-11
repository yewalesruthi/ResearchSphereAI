import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SettingsState {
  llmModel: string;
  embeddingModel: string;
  groqApiKey: string;
  setLlmModel: (model: string) => void;
  setEmbeddingModel: (model: string) => void;
  setGroqApiKey: (key: string) => void;
}

export const GROQ_MODELS = [
  "llama-3.3-70b-versatile",
  "llama-3.1-8b-instant",
  "mixtral-8x7b-32768",
  "gemma2-9b-it",
];

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      llmModel: "llama-3.3-70b-versatile",
      embeddingModel: "BAAI/bge-small-en-v1.5",
      groqApiKey: "",
      setLlmModel: (model) => set({ llmModel: model }),
      setEmbeddingModel: (model) => set({ embeddingModel: model }),
      setGroqApiKey: (key) => set({ groqApiKey: key }),
    }),
    { name: "settings-storage" }
  )
);
