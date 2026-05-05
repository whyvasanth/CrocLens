# CrocLens Database Schema

## Current Status

Phase 0 defines the planned database shape. The actual PostgreSQL schema will be implemented in Phase 4.

## Database Goal

The database must support a user's full financial picture, not only stocks.

It needs to represent:

- Assets
- Liabilities
- Real estate
- Retirement accounts
- Tax lots
- Market prices
- Watchlist items
- Decision journal entries
- AI outputs

## Planned Tables

### users

Represents an account in the system.

Key fields later:

- `id`
- `email`
- `created_at`
- `updated_at`

### user_profiles

Stores beginner profile, goals, risk tolerance, and preferences.

### portfolios

Groups a user's holdings and accounts.

### assets

Stores asset metadata for stocks, ETFs, mutual funds, crypto, cash, bonds, and other asset types.

### holdings

Stores what the user owns.

Examples:

- Stock shares
- ETF shares
- Mutual fund units
- Crypto quantity
- Cash amount
- Bond face value

### liabilities

Stores what the user owes.

Examples:

- Mortgage
- Student loan
- Credit card debt
- Personal loan

### real_estate_properties

Stores property-specific fields such as estimated value, mortgage balance, location context, and ownership share.

### retirement_accounts

Stores 401(k), IRA, Roth IRA, pension, and similar account details.

### decision_journal_entries

Stores user decisions and later review outcomes.

### action_plans

Stores generated or user-approved educational action plans.

### agent_outputs

Stores AI responses, confidence, data limitations, sources, and safety metadata.

### market_prices

Stores prices and source metadata for assets.

### news_articles

Stores news data used for impact analysis.

### watchlist_items

Stores assets or markets the user wants to watch.

### tax_lots

Stores purchase lots for tax-aware explanations.

### asset_scores

Stores risk, liquidity, diversification, yield, inflation sensitivity, and tax complexity scores.

## Core Relational Concepts

Primary key:

- A unique ID for each row.

Foreign key:

- A link from one table to another table.

Index:

- A data structure that makes common queries faster.

Migration:

- A versioned database change that can be applied consistently across environments.

## Why This Schema Supports Cross-Asset Wealth

CrocLens separates generic concepts from asset-specific concepts.

Generic:

- `assets`
- `holdings`
- `market_prices`
- `asset_scores`

Specific:

- `real_estate_properties`
- `retirement_accounts`
- `liabilities`
- `tax_lots`

This lets the product compare different asset types while still storing details that only apply to certain assets.

