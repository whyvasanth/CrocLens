import { NextResponse } from "next/server";
import type { AccountUserResponse } from "@/types/api";
import { backendJson, getSessionToken } from "../_shared";

export async function GET() {
  const token = await getSessionToken();
  if (!token) {
    return NextResponse.json({ detail: "Authentication is required." }, { status: 401 });
  }

  const backendResponse = await backendJson<AccountUserResponse, never>("/api/v1/auth/me", {
    token
  });
  const payload = await backendResponse.json();
  return NextResponse.json(payload, { status: backendResponse.status });
}
