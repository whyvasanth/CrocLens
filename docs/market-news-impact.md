# Phase 12: Market, News, And Personal Impact

## What We Built

Phase 12 adds the first "How does this affect me?" workflow.

The API returns:

- Sample news articles.
- Holdings that may be affected.
- Plain-language impact explanations.
- Safe suggested questions.
- Confidence, sources, limitations, and educational disclaimer.

The frontend adds:

- `/market-news`
- A sidebar link.
- A clean impact summary page.

## Why This Matters

Beginners often see financial headlines without knowing whether the news matters to their own money. CrocLens should connect headlines to portfolio context without turning news into trading advice.

## System Design Concept

The workflow separates:

- News context.
- Portfolio holdings.
- Impact mapping logic.
- User-facing explanation.

This keeps the system testable and safer than letting an AI answer directly from raw headlines.

## Safety Rule

News impact is educational only. CrocLens should say what may be worth reviewing, not what to buy or sell.

## Endpoint

```http
GET /api/v1/market-news/impact-summary
```

## Mini Assignment

Add one more sample article about inflation and map it to cash, bonds, real estate, and retirement.
