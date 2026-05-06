# Phase 16: Watchlist Intelligence

## What We Built

Phase 16 adds watchlist intelligence.

Users can track:

- Stocks.
- ETFs.
- Crypto.
- Real estate markets.
- Bonds and Treasuries.
- Other research topics.

Each item includes:

- Why the user is watching it.
- AI-style educational summary.
- Risk notes.
- Opportunity notes.
- Confidence and limitations.

## Why This Matters

A watchlist should be a research list, not a buy list. CrocLens uses the watchlist to teach users how to compare an asset with goals, risk, liquidity, taxes, and source freshness.

## Endpoints

```http
GET /api/v1/watchlist
POST /api/v1/watchlist
```

## Mini Assignment

Add a real estate market watchlist item and write one risk note tied to local data limitations.
