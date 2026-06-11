import axios, { isAxiosError } from "axios";
import { useAuthStore } from "@/store/authStore";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = sessionStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (isAxiosError(error) && !error.response) {
      error.message = "Network Error";
      (error as { isNetworkError?: boolean }).isNetworkError = true;
    }
    if (error.response?.status === 401 && typeof window !== "undefined") {
      useAuthStore.getState().logout();
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export function isNetworkError(error: unknown): boolean {
  if (!isAxiosError(error)) return false;
  return (error as { isNetworkError?: boolean }).isNetworkError === true || !error.response;
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    await api.get("/health", { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}

export function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (typeof window !== "undefined") {
    const token = sessionStorage.getItem("token");
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (isAxiosError(error) && !error.response) {
    return `Connection failed. Ensure the backend is running at ${API_URL}. Open the app at http://localhost:3000 (not 127.0.0.1).`;
  }
  return fallback;
}

export { API_URL };
export default api;
