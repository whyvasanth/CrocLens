# CrocLens AI Agents

## AI Strategy

CrocLens will not start with a complex agent system.

The safe build order is:

1. Mock AI responses
2. Rule-based assistant responses
3. LLM-ready prompt templates
4. Structured outputs with safety fields
5. Specialist agents
6. Multi-agent orchestration

This keeps the product understandable and testable before adding more AI complexity.

## Phase 9 Assistant v1

Phase 9 implements the first real assistant structure without calling an external LLM.

Implemented pieces:

- Rule-based intent routing
- Grounded context builder
- Prompt versioning
- Safety checks for direct trading and guaranteed-return wording
- Structured assistant response fields
- Croc Guide frontend integration
- Authenticated grounding from portfolio, liabilities, profile, watchlist, journal, action plans, retirement accounts, tax lots, and stored market freshness when a session is present

The current prompt version is:

```text
assistant_v3_grounded_context_2026_06_23
```

The assistant can route:

- Portfolio questions
- Debt questions
- Retirement questions
- Tax questions
- Market questions
- Risk questions
- Beginner education questions
- Safety-sensitive questions

## Phase 10 Lightweight Orchestrator

Phase 10 adds deterministic multi-agent orchestration.

Current flow:

```text
User question
  -> Intent Router Agent
  -> Grounded context builder, using authenticated records when available
  -> Specialist Agent
  -> Action Plan Agent
  -> Safety/Compliance Guardrail Agent
  -> Croc Guide response with evidence, source freshness, and collapsed trace metadata
```

For safety-sensitive questions, the flow skips the specialist and goes directly from the Intent Router Agent to the Safety/Compliance Guardrail Agent.

Implemented agents:

- Intent Router Agent
- Portfolio Analyst Agent
- News Impact Agent
- Tax-Aware Agent
- Retirement Planner Agent
- Debt/Liability Coach Agent
- Action Plan Agent
- Safety/Compliance Guardrail Agent

Stubbed agents:

- Cross-Asset Comparison Agent
- Stock/ETF Research Agent
- Crypto Research Agent
- Real Estate Insight Agent
- Decision Journal Feedback Agent

Why deterministic first:

- Easier to test
- No model cost
- No hidden LLM behavior
- Clear trace output
- Same contract can later be implemented with LangGraph nodes

## Phase 24 Grounded Croc Guide

Phase 24 keeps Croc Guide deterministic by default but grounds responses in the user's saved records.

Context inputs:

- Current authenticated user and risk profile
- Holdings and liabilities
- Allocation, concentration, risk, and diversification scores
- Stored market observation freshness
- Watchlist items
- Decision journal status
- Action plan lifecycle status
- Retirement accounts
- Tax lots

Safety boundaries:

- Croc Guide does not call paid LLMs by default.
- Croc Guide does not expose internal prompts.
- Unsafe requests return safe categories such as `direct_trading_instruction`, `return_claim`, or `prompt_injection_attempt`.
- Raw user prompt text is not copied into the returned trace.
- Missing data is described as missing rather than replaced with hidden sample data.

## AI Output Contract

Every assistant output should follow a structure like this:

```json
{
  "summary": "Beginner-friendly explanation.",
  "observations": ["Fact from saved records."],
  "why_it_matters": "Plain-language reason this matters.",
  "considerations": ["Educational item to review."],
  "evidence": [
    {
      "label": "Net worth",
      "value": "$12,500",
      "source_name": "CrocLens portfolio records",
      "data_as_of": "2026-06-23",
      "is_sample_data": false,
      "data_quality": "user_entered",
      "provider_status": "manual_only",
      "is_stale": false
    }
  ],
  "confidence": "medium",
  "data_as_of": "2026-06-23",
  "is_sample_data": false,
  "data_quality": "user_entered",
  "provider_status": "manual_only",
  "is_stale": false,
  "data_limitations": ["Uses saved records only."],
  "sources": [
    {
      "name": "Manual entry",
      "as_of_date": "2026-05-05"
    }
  ],
  "safety_disclaimer": "This is educational, not financial advice."
}
```

## Required Safety Behavior

The assistant must:

- Use safe educational wording.
- Include confidence and limitations.
- Explain assumptions.
- Refuse direct buy/sell commands.
- Avoid guaranteed returns.
- Avoid pretending to be a licensed advisor.
- Avoid echoing prompt-injection or trading-command text back to the user.
- Include evidence and data freshness when available.

## Agent List

### 1. Intent Router Agent

Purpose:

- Decide what the user is asking.
- Route the request to the right specialist.

Example intents:

- Portfolio review
- Tax question
- Retirement question
- Debt question
- News impact question

### 2. Portfolio Analyst Agent

Purpose:

- Explain net worth, allocation, performance, diversification, and risk.

### 3. Cross-Asset Comparison Agent

Purpose:

- Compare assets such as stocks, crypto, real estate, cash, bonds, and liabilities.

### 4. Stock/ETF Research Agent

Purpose:

- Explain stock and ETF information in beginner-friendly language.

### 5. Crypto Research Agent

Purpose:

- Explain crypto assets, volatility, liquidity, and risk.

### 6. Real Estate Insight Agent

Purpose:

- Explain property equity, mortgage impact, local housing context, and concentration risk.

### 7. News Impact Agent

Purpose:

- Answer "How does this affect me?" using user holdings and news context.

### 8. Tax-Aware Agent

Purpose:

- Explain tax lots, holding periods, unrealized gains/losses, and tax-loss harvesting concepts.

Safety:

- Must say it is educational, not tax advice.

### 9. Retirement Planner Agent

Purpose:

- Explain retirement progress, contribution rates, employer match, and scenario assumptions.

### 10. Debt/Liability Coach Agent

Purpose:

- Explain debt balances, rates, payoff tradeoffs, and risk.

### 11. Action Plan Agent

Purpose:

- Convert insights into safe next-step checklists.

Safe wording:

- "Consider reviewing..."
- "You may want to compare..."
- "This may be worth discussing with a professional..."

### 12. Decision Journal Feedback Agent

Purpose:

- Help users learn from past decisions by comparing expected and actual outcomes.

### 13. Safety/Compliance Guardrail Agent

Purpose:

- Review all AI output before it reaches the user.
- Block unsafe trading instructions.
- Add missing disclaimers or limitations.

## Future Orchestration Flow

```text
User asks question
  |
  v
Intent Router Agent
  |
  +--> Portfolio Analyst Agent
  +--> Tax-Aware Agent
  +--> Retirement Planner Agent
  +--> News Impact Agent
  |
  v
Action Plan Agent, if next steps are needed
  |
  v
Safety/Compliance Guardrail Agent
  |
  v
Structured response to frontend
```

## Why Multi-Agent Later

Multi-agent systems help when different tasks require different context, tools, or safety rules.

They also add complexity:

- More routing logic
- More failure modes
- More tests
- More cost
- More observability needs

That is why CrocLens starts with one simple assistant endpoint first.
