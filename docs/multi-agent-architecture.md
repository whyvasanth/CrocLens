# Multi-Agent Architecture

Phase 10 adds CrocLens' first multi-agent architecture.

## Goal

The assistant should not be one opaque function forever. As CrocLens grows, different questions need different expertise:

- Portfolio analysis
- Debt coaching
- Tax-aware explanations
- Retirement planning
- News impact analysis
- Safety review

Phase 10 introduces those roles without adding external model cost or LangGraph complexity yet.

## Current Orchestration Flow

```text
User question
  |
  v
Intent Router Agent
  |
  v
Specialist Agent
  |
  v
Action Plan Agent
  |
  v
Safety/Compliance Guardrail Agent
  |
  v
Structured assistant response
```

Safety-sensitive questions skip the specialist and go directly to the guardrail.

## Agent State

The current state is small and explicit:

- User question
- Routed intent
- Specialist answer summary
- Suggested next steps
- Safety result
- Tools used
- Trace output

Later, this state can become a LangGraph state object.

## Tool Use

Phase 10 tool use is simulated by naming the structured data each agent depends on:

- `portfolio_summary`
- `asset_allocation`
- `asset_scores`
- `liability_summary`
- `tax_lot_stub`
- `retirement_account_stub`
- `unsafe_language_rules`

This keeps the contract visible before real tool calls become complex.

## Why This Helps

Multi-agent systems help when:

- Different tasks need different context.
- Safety review should be separate from answer generation.
- Tool access needs to be controlled.
- Engineers need traces for debugging and evaluation.

They also add risk:

- More routing bugs
- More latency
- More tests
- More observability needs
- More model cost later

That is why CrocLens starts with a deterministic orchestrator.
