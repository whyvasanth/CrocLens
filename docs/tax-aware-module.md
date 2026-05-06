# Phase 13: Tax-Aware Module

## What We Built

Phase 13 adds educational tax-aware insights.

The backend returns:

- Sample tax lots.
- Unrealized gain/loss calculations.
- Short-term versus long-term holding labels.
- Tax-loss harvesting education.
- Wash-sale warning language.

The frontend replaces the Tax Planner placeholder with an API-backed page.

## Why This Matters

Beginners often hear about taxes only after selling. CrocLens should teach that tax lots, holding periods, gains, losses, and wash-sale rules can matter before a decision is made.

## Safety Rule

CrocLens does not give tax advice. It explains concepts and tells users when a topic may be worth discussing with a tax professional.

## Endpoint

```http
GET /api/v1/tax/insights
```

## Mini Assignment

Add one more tax lot and explain whether it is short-term or long-term.
