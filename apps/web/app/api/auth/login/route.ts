import { NextRequest, NextResponse } from "next/server";
import type { AccountLoginRequest, AccountSessionResponse } from "@/types/api";
import { backendJson, setSessionCookie, toBrowserSession } from "../_shared";

export async function POST(request: NextRequest) {
  const body = (await request.json()) as AccountLoginRequest;
  const backendResponse = await backendJson<AccountSessionResponse, AccountLoginRequest>("/api/v1/auth/login", {
    body,
    method: "POST"
  });
  const payload = await backendResponse.json();

  if (!backendResponse.ok) {
    return NextResponse.json(payload, { status: backendResponse.status });
  }

  await setSessionCookie(payload as AccountSessionResponse);
  return NextResponse.json(toBrowserSession(payload as AccountSessionResponse));
}
