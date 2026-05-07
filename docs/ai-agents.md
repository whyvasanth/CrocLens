# CrocLens AI Agents

## Phase 21 Efficient Agent Architecture

Phase 21 replaces the earlier 13-agent conceptual list with 8 focused agents:

- Router Agent
- Wealth Analyst Agent
- Market Research Agent
- Life Planning Agent
- Tax Awareness Agent
- Action Plan Agent
- Decision Journal Agent
- Safety Guardrail Agent

Merged agents:

- Portfolio Analyst and Cross-Asset Comparison are now Wealth Analyst.
- Stock/ETF Research, Crypto Research, News Impact, and macro context are now Market Research.
- Retirement Planner and Debt/Liability Coach are now Life Planning.
- Real Estate Insight is handled through Wealth Analyst and Life Planning until richer real estate data exists.

Runtime rules:

- Default `LLM_MODE=mock` keeps the app deterministic and free.
- LLMs may explain and synthesize, but they must not calculate money values by themselves.
- Agents can only use allowlisted provider tools.
- The Safety Guardrail Agent always runs last.
- Responses include summary, reasoning summary, action items, risks, confidence, data sources, freshness, limitations, and disclaimer.

New endpoints:

```http
POST /api/v1/ai/chat
POST /api/v1/ai/action-plan
POST /api/v1/ai/explain-asset
POST /api/v1/ai/portfolio-review
```

The legacy endpoint remains:

```http
POST /api/v1/ai/assistant
```

It forwards into the Phase 21 orchestrator and maps back to the older response shape for frontend compatibility.

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
- Prompt context builder
- Prompt versioning
- Safety checks for direct trading and guaranteed-return wording
- Structured assistant response fields
- Croc Guide frontend integration

The current prompt version is:

```text
assistant_v1_rule_based_2026_05_05
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
  -> Specialist Agent
  -> Action Plan Agent
  -> Safety/Compliance Guardrail Agent
  -> Croc Guide response with agent trace
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

## AI Output Contract

Every AI output should eventually follow a structure like this:

```json
{
  "summary": "Beginner-friendly explanation.",
  "considerations": ["Educational item to review."],
  "confidence": "medium",
  "data_limitations": ["Uses sample data."],
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
