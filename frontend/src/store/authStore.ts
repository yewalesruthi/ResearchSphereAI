import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      setAuth: (user, token) => {
        sessionStorage.setItem("token", token);
        set({ user });
      },
      logout: () => {
        sessionStorage.removeItem("token");
        set({ user: null });
      },
      isAuthenticated: () => !!get().user,
    }),
    { name: "auth-storage", partialize: (state) => ({ user: state.user }) }
  )
);
