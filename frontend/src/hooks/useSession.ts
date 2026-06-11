"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import type { User } from "@/types";

export function useSession() {
  const { user, setAuth, logout, isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const restore = async () => {
      try {
        const res = await api.get<User>("/auth/me");
        const token = sessionStorage.getItem("token") ?? "";
        setAuth(res.data, token);
      } catch {
        if (user) logout();
      } finally {
        setLoading(false);
      }
    };
    restore();
    // Only run on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { loading, isAuthenticated: isAuthenticated() };
}
