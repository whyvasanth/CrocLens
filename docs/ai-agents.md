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

