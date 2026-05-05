# CrocLens Evaluation Metrics

## Current Status

Phase 0 defines the metrics direction. Product and AI evaluation work will happen in Phase 19.

## Why Metrics Matter

CrocLens is an AI fintech education product. It needs to be useful, understandable, reliable, and safe.

Metrics help answer:

- Are users completing onboarding?
- Are users creating portfolios?
- Are AI explanations clear?
- Are AI outputs safe?
- Is data fresh?
- Is the API reliable?

## Product Metrics

Potential metrics:

- Onboarding completion rate
- Portfolio creation rate
- Manual asset entry completion
- Watchlist usage
- Action plan usage
- Decision journal usage
- Return visits

## AI Quality Metrics

Potential metrics:

- AI clarity score
- Unsafe recommendation rate
- Missing disclaimer rate
- Missing confidence rate
- Missing data limitation rate
- Hallucination check failures
- User helpfulness feedback

## Data Metrics

Potential metrics:

- Data freshness by source
- Failed ingestion jobs
- Duplicate records
- Missing prices
- Unknown symbols
- Stale source warnings shown

## Reliability Metrics

Potential metrics:

- API latency
- API error rate
- Frontend build failures
- Backend test failures
- Database migration failures
- AI response validation failures

## Evaluation Rule

Every AI feature should be evaluated for both usefulness and safety.

A response that sounds confident but lacks limitations or gives direct trading instructions should fail evaluation, even if it is fluent.

