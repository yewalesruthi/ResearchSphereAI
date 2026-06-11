"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import type { AuthResponse } from "@/types";

export function useAuth() {
  const router = useRouter();
  const { user, setAuth, logout: clearAuth, isAuthenticated } = useAuthStore();

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await api.post<AuthResponse>("/auth/login", { email, password });
      setAuth(res.data.user, res.data.access_token);
      router.push("/dashboard");
    },
    [setAuth, router]
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const res = await api.post<AuthResponse>("/auth/register", { email, password });
      setAuth(res.data.user, res.data.access_token);
      router.push("/dashboard");
    },
    [setAuth, router]
  );

  const logout = useCallback(async () => {
    try {
      await api.post("/auth/logout");
    } finally {
      clearAuth();
      router.push("/login");
    }
  }, [clearAuth, router]);

  return { user, login, register, logout, isAuthenticated };
}
