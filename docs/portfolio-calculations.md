# CrocLens Portfolio Calculations

## Current Status

Phase 6 implements transparent MVP portfolio calculations in:

```text
apps/api/app/services/portfolio_calculations.py
```

These formulas are educational heuristics, not financial advice. They are intentionally simple so they can be tested, explained, and replaced later.

## Inputs

The calculation service currently accepts:

- Asset positions
- Liability positions

An asset position includes:

- `asset_class`
- `market_value`

A liability position includes:

- `liability_type`
- `balance`
- optional `interest_rate`

## Core Totals

Total assets:

```text
sum(asset.market_value)
```

Total liabilities:

```text
sum(liability.balance)
```

Net worth:

```text
total_assets - total_liabilities
```

## Asset Allocation

Allocation by asset class:

```text
asset_class_market_value / total_assets * 100
```

Example:

```text
Stocks percent = stock_market_value / total_assets * 100
```

## Debt Impact

Debt-to-asset percent:

```text
total_liabilities / total_assets * 100
```

Beginner meaning:

- Higher debt impact means liabilities are a larger share of tracked assets.
- This does not automatically mean something is bad.
- It means the user may want to understand how debt affects net worth.

## Score Formulas

Most scores use a market-value-weighted asset-class formula:

```text
sum(asset market value * asset-class weight) / total assets
```

The current weights live in code so they can be reviewed and tested.

### Risk Score

What it means:

- Higher means the asset mix may move more in value.

Formula:

```text
sum(asset market value * asset-class risk weight) / total assets
```

### Liquidity Score

What it means:

- Higher means more of the portfolio is in assets that are usually easier to access or sell.

Formula:

```text
sum(asset market value * asset-class liquidity weight) / total assets
```

### Diversification Score

What it means:

- Higher means the portfolio is spread across more asset classes and is less concentrated.

Formula:

```text
40 + min(asset class count, 6) * 8 - concentration penalty
```

Concentration penalty:

```text
max(0, largest_allocation_percent - 35) * 1.2
```

### Income/Yield Score

What it means:

- Higher means the asset mix may produce more interest, dividends, rent, or yield.

Formula:

```text
sum(asset market value * asset-class income/yield weight) / total assets
```

### Inflation Resilience Score

What it means:

- Higher means the asset mix may be less exposed to inflation eroding purchasing power.

Formula:

```text
sum(asset market value * asset-class inflation-resilience weight) / total assets
```

### Tax Complexity Score

What it means:

- Higher means the asset mix may require more tax tracking.
- This is not a good/bad score. It is a complexity signal.

Formula:

```text
sum(asset market value * asset-class tax-complexity weight) / total assets
```

## Why These Are MVP Heuristics

These formulas are useful for learning and product shape, but they are not final financial models.

Production improvements could include:

- User risk profile
- Time horizon
- Tax account type
- Security-level volatility
- Real yield data
- Debt interest rates
- Historical drawdowns
- Confidence intervals
- Data freshness weighting

## Safety Language

CrocLens should explain scores with safe wording:

- "This may indicate..."
- "Consider reviewing..."
- "Based on the data provided..."
- "This is educational, not financial advice."

Avoid:

- "Buy this"
- "Sell this"
- "Guaranteed"
- "Best investment"

