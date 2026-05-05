# Onboarding and Risk Profile

Phase 8 adds the first CrocLens personalization flow.

## Goal

The onboarding flow collects beginner-friendly context:

- Investing experience
- Primary goal
- Risk tolerance
- Time horizon
- Income range
- Emergency cash months
- Retirement account status
- Employer match awareness
- Debt and liability context
- Manual asset entries

## System Design

```text
Frontend onboarding page
  -> controlled React form
  -> POST /api/v1/onboarding/profile

FastAPI onboarding route
  -> validates request with Pydantic
  -> calls onboarding service
  -> returns educational risk profile
```

## Risk Scoring

The MVP score is intentionally simple:

- Start with risk tolerance.
- Adjust for investing experience.
- Adjust for time horizon.
- Adjust for primary goal.
- Adjust for emergency cash.
- Adjust for high-interest debt.

The output is a beginner profile:

- `Cautious Beginner`
- `Balanced Beginner`
- `Growth-Oriented Beginner`

This is a heuristic. It is not financial advice.

## Why This Matters

Production AI products need structured user context. Later phases can pass this onboarding profile into:

- Dashboard explanations
- Action plan generation
- Croc Guide prompt context
- Retirement planning
- Debt coaching
- Safety guardrails

## Safety Rules

The onboarding response must:

- Use educational language.
- Include confidence.
- Include data limitations.
- Avoid direct investment instructions.
- Avoid guaranteed outcomes.
