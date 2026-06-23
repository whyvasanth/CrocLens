import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AccountAuthPage } from "./account-auth-page";
import type { BrowserAccountSessionResponse } from "@/types/api";

const navigationMocks = vi.hoisted(() => ({
  push: vi.fn()
}));

const apiMocks = vi.hoisted(() => ({
  createAccount: vi.fn(),
  loginAccount: vi.fn()
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: navigationMocks.push
  })
}));

vi.mock("@/lib/api-client", () => apiMocks);

function sessionResponse(): BrowserAccountSessionResponse {
  return {
    user: {
      beginner_mode_enabled: true,
      created_at: "2026-06-23T12:00:00Z",
      display_name: "Test User",
      email: "test@croclens.local",
      id: "user-test"
    },
    onboarding_profile: null,
    expires_in_minutes: 120,
    next_path: "/dashboard",
    confidence: "high",
    data_limitations: ["Local test session."],
    sources: [{ name: "CrocLens local auth", freshness: "current", as_of: "2026-06-23" }],
    security_note: "Session stored in a secure browser cookie.",
    token_type: "local_cookie_session"
  };
}

describe("AccountAuthPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows friendly signup validation before calling the API", async () => {
    const user = userEvent.setup();

    render(<AccountAuthPage mode="signup" />);

    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(screen.getByText(/please enter your name/i)).toBeTruthy();
    expect(apiMocks.createAccount).not.toHaveBeenCalled();
  });

  it("logs in with normalized email and redirects to the returned path", async () => {
    const user = userEvent.setup();
    apiMocks.loginAccount.mockResolvedValue(sessionResponse());

    render(<AccountAuthPage mode="login" />);

    await user.type(screen.getByLabelText(/email/i), " TEST@CROCLENS.LOCAL ");
    await user.type(screen.getByLabelText(/password/i), "strongpassword123");
    await user.click(screen.getByRole("button", { name: /^log in$/i }));

    await waitFor(() => {
      expect(apiMocks.loginAccount).toHaveBeenCalledWith({
        email: "test@croclens.local",
        password: "strongpassword123"
      });
    });
    expect(navigationMocks.push).toHaveBeenCalledWith("/dashboard");
  });
});
