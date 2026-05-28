import type { DashboardSummary, ChatResponse } from "./types";

// Empty string = same-origin. The Next.js API proxy at /api/[...path] forwards
// to BACKEND_URL (a server-side env var). For direct local dev without the proxy,
// set NEXT_PUBLIC_API_URL=http://localhost:8000 in frontend/.env.local.
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  getDashboardSummary: () => apiFetch<DashboardSummary>("/api/dashboard/summary"),
  chat: (message: string, sessionId?: string) =>
    apiFetch<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, session_id: sessionId }),
    }),
};
