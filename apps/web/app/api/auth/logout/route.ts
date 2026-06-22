import { NextResponse } from "next/server";
import type { LogoutResponse } from "@/types/api";
import { backendJson, clearSessionCookie, getSessionToken } from "../_shared";

export async function POST() {
  const token = await getSessionToken();
  if (token) {
    await backendJson<LogoutResponse, never>("/api/v1/auth/logout", {
      method: "POST",
      token
    });
  }

  await clearSessionCookie();
  return NextResponse.json({ status: "logged_out" } satisfies LogoutResponse);
}
