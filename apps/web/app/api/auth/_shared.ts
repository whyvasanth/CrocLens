import { cookies } from "next/headers";
import type {
  AccountSessionResponse,
  BrowserAccountSessionResponse
} from "@/types/api";

export const SESSION_COOKIE_NAME = "croclens_session";

export function getBackendBaseUrl() {
  return (
    process.env.CROCLENS_API_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    process.env.NEXT_PUBLIC_CROCLENS_API_URL ??
    "http://127.0.0.1:8000"
  );
}

export async function getSessionToken() {
  const cookieStore = await cookies();
  return cookieStore.get(SESSION_COOKIE_NAME)?.value ?? null;
}

export async function setSessionCookie(session: AccountSessionResponse) {
  const cookieStore = await cookies();
  cookieStore.set({
    name: SESSION_COOKIE_NAME,
    value: session.session_token,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: session.expires_in_minutes * 60
  });
}

export async function clearSessionCookie() {
  const cookieStore = await cookies();
  cookieStore.set({
    name: SESSION_COOKIE_NAME,
    value: "",
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0
  });
}

export function toBrowserSession(session: AccountSessionResponse): BrowserAccountSessionResponse {
  return {
    user: session.user,
    onboarding_profile: session.onboarding_profile,
    token_type: "local_cookie_session",
    expires_in_minutes: session.expires_in_minutes,
    next_path: session.next_path,
    confidence: session.confidence,
    data_limitations: [
      ...session.data_limitations,
      "The browser receives session metadata only. The raw local session token is stored in an HttpOnly cookie."
    ],
    sources: session.sources,
    security_note: session.security_note
  };
}

export async function backendJson<TResponse, TRequest>(
  path: string,
  init: {
    body?: TRequest;
    method?: "GET" | "POST";
    token?: string | null;
  } = {}
): Promise<Response> {
  const response = await fetch(`${getBackendBaseUrl()}${path}`, {
    body: init.body ? JSON.stringify(init.body) : undefined,
    cache: "no-store",
    headers: {
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...(init.token ? { Authorization: `Bearer ${init.token}` } : {})
    },
    method: init.method ?? "GET"
  });

  return response;
}
