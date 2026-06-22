# AI Assistant v1

Phase 9 adds the first API-backed Croc Guide assistant.

## Goal

The assistant should answer beginner money questions safely. When a user is signed in, it uses that user's persisted PostgreSQL portfolio records. When no session is present, it falls back to CrocLens sample dashboard context.

It does not call an external LLM yet.

## Architecture

```text
Croc Guide drawer
  -> POST /api/backend/api/v1/ai/assistant
  -> Next.js BFF forwards HttpOnly cookie session
  -> FastAPI route with optional current user
  -> assistant service
  -> intent router
  -> portfolio context builder
  -> safety check
  -> structured response
```

## Why Rule-Based First

Rule-based logic is easier to test and cheaper to run. It lets us design:

- Response contracts
- Safety fields
- Prompt structure
- Frontend rendering
- Tests

before adding a model provider.

## Prompt Context

Assistant v1 builds a prompt context with:

- Prompt version
- Intent
- System safety rules
- Portfolio context summary
- User question

Context sources:

- Signed-in users: manually entered holdings and liabilities from PostgreSQL.
- Demo visitors: CrocLens sample dashboard data.

Later, this can become the input to an LLM.

## Safety Behavior

The assistant detects wording such as:

- Direct buy/sell requests
- Guaranteed-return language
- Claims about the best investment

When detected, it reframes the answer into educational review language.

## Output Contract

Each response includes:

- Intent
- Summary
- Beginner explanation
- Suggested next steps
- Confidence
- Data limitations
- Sources
- Safety check result
- Optional prompt context
- Educational disclaimer
