import { NextResponse } from "next/server";
import type { AccountUserResponse } from "@/types/api";
import { backendJson, clearSessionCookie, getSessionToken } from "../_shared";

export async function GET() {
  const token = await getSessionToken();
  if (!token) {
    return NextResponse.json(null);
  }

  const backendResponse = await backendJson<AccountUserResponse, never>("/api/v1/auth/me", {
    token
  });
  const payload = await backendResponse.json();

  if (backendResponse.status === 401) {
    await clearSessionCookie();
    return NextResponse.json(null);
  }

  return NextResponse.json(payload, { status: backendResponse.status });
}
