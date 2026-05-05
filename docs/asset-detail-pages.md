# Asset Detail Pages

Phase 7 adds beginner-friendly detail pages for the major CrocLens wealth item types.

## Goal

The dashboard tells the user what is happening at a high level. Detail pages explain why each asset or liability matters.

The MVP covers:

- Stocks and ETFs
- Crypto
- Real estate
- Debt and liabilities
- Retirement accounts

## System Design

```text
Portfolio page
  -> GET /api/v1/assets/detail-cards
  -> links to /assets/{asset_id}

Asset detail page
  -> GET /api/v1/assets/{asset_id}/detail
  -> renders beginner explanations, metrics, safety fields, and limitations
```

## Why the Backend Owns the Detail Copy

The backend response model keeps the product contract explicit. Later, these fields can be generated from database records, market data, and AI agent outputs without redesigning the frontend.

Each detail response includes:

- What this asset is
- Why it matters
- Risk explanation
- Liquidity explanation
- Tax complexity explanation
- Income potential explanation
- What to watch
- Safe next steps
- Confidence
- Data limitations
- Source freshness
- Educational disclaimer

## Safety Rules

Detail pages must avoid direct trading instructions. They should use educational language such as:

- "Consider reviewing..."
- "You may want to research..."
- "This could be a risk..."
- "This may be worth discussing with a professional..."

The page should not say:

- "Buy this"
- "Sell this"
- "Guaranteed return"
- "Best investment"
