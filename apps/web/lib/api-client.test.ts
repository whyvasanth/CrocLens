import { afterEach, describe, expect, it, vi } from "vitest";
import { getMarketSnapshot, loginAccount } from "./api-client";

describe("api-client BFF routing", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("routes backend API calls through the Next.js backend proxy", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          data_limitations: [],
          data_quality: "saved",
          educational_disclaimer: "Educational information only.",
          is_sample_data: false,
          items: [],
          provider_status: "available"
        }),
        { headers: { "Content-Type": "application/json" }, status: 200 }
      )
    );
    vi.stubGlobal("fetch", fetchMock);

    await getMarketSnapshot();

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/backend/api/v1/market/snapshot",
      expect.objectContaining({
        headers: {
          Accept: "application/json"
        }
      })
    );
  });

  it("keeps login on the local auth BFF route", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          confidence: "high",
          data_limitations: [],
          expires_in_minutes: 120,
          next_path: "/dashboard",
          onboarding_profile: null,
          security_note: "Session stored in a secure browser cookie.",
          sources: [],
          token_type: "local_cookie_session",
          user: {
            beginner_mode_enabled: true,
            created_at: "2026-06-23T12:00:00Z",
            display_name: "Test User",
            email: "test@croclens.local",
            id: "user-test"
          }
        }),
        { headers: { "Content-Type": "application/json" }, status: 200 }
      )
    );
    vi.stubGlobal("fetch", fetchMock);

    await loginAccount({ email: "test@croclens.local", password: "strongpassword123" });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/auth/login",
      expect.objectContaining({
        body: JSON.stringify({ email: "test@croclens.local", password: "strongpassword123" }),
        method: "POST"
      })
    );
  });
});
