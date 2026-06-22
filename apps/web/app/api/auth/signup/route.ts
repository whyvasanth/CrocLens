import { NextRequest, NextResponse } from "next/server";
import type { AccountCreateRequest, AccountSessionResponse } from "@/types/api";
import { backendJson, setSessionCookie, toBrowserSession } from "../_shared";

export async function POST(request: NextRequest) {
  const body = (await request.json()) as AccountCreateRequest;
  const backendResponse = await backendJson<AccountSessionResponse, AccountCreateRequest>("/api/v1/auth/signup", {
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
