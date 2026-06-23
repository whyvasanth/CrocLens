import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CrocGuidePanel } from "./croc-guide-panel";
import type { AssistantResponse } from "@/types/api";

const apiMocks = vi.hoisted(() => ({
  askAssistant: vi.fn()
}));

vi.mock("@/lib/api-client", () => apiMocks);

function assistantResponse(): AssistantResponse {
  return {
    intent: "portfolio",
    summary: "Your portfolio is spread across a few asset types.",
    observations: ["Stocks are the largest visible allocation.", "Debt lowers your net worth."],
    why_it_matters: "Diversification can reduce reliance on one part of your financial life.",
    considerations: ["Consider reviewing concentration before making new decisions."],
    beginner_explanation: "CrocLens compares your saved assets and debts in simple terms.",
    suggested_next_steps: ["Review your largest holding.", "Check whether debt payments fit your goals."],
    evidence: [
      {
        label: "Net worth",
        value: "$214,800",
        source_name: "CrocLens records",
        data_as_of: "2026-06-23",
        retrieved_at: "2026-06-23T12:00:00Z",
        is_sample_data: false,
        data_quality: "saved",
        provider_status: "available",
        is_stale: false,
        limitations: ["Manual records may need updates."]
      }
    ],
    confidence: "medium",
    data_as_of: "2026-06-23",
    retrieved_at: "2026-06-23T12:00:00Z",
    is_sample_data: false,
    data_quality: "saved",
    provider_status: "available",
    is_stale: false,
    data_limitations: ["Manual records may need updates."],
    sources: [{ name: "CrocLens records", freshness: "saved", as_of: "2026-06-23" }],
    safety: {
      passed: true,
      flags: [],
      rewritten_question: null
    },
    agent_trace: [],
    prompt_context: null,
    educational_disclaimer: "Educational information only, not financial advice.",
    safety_disclaimer: "CrocLens does not provide direct buy or sell instructions."
  };
}

describe("CrocGuidePanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("submits a user question and renders the grounded answer", async () => {
    const user = userEvent.setup();
    apiMocks.askAssistant.mockResolvedValue(assistantResponse());

    render(<CrocGuidePanel isOpen onClose={vi.fn()} />);

    await user.clear(screen.getByLabelText(/ask croclens/i));
    await user.type(screen.getByLabelText(/ask croclens/i), "How diversified am I?");
    await user.click(screen.getByRole("button", { name: /send question/i }));

    await waitFor(() => {
      expect(apiMocks.askAssistant).toHaveBeenCalledWith({
        beginner_mode: true,
        include_prompt_debug: false,
        question: "How diversified am I?"
      });
    });

    expect(screen.getByText(/your portfolio is spread/i)).toBeTruthy();
    expect(screen.getByText(/how croclens reached this/i)).toBeTruthy();
    expect(screen.getByText(/educational information only/i)).toBeTruthy();
  });

  it("closes with the Escape key", () => {
    const onClose = vi.fn();

    render(<CrocGuidePanel isOpen onClose={onClose} />);
    fireEvent.keyDown(window, { key: "Escape" });

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
