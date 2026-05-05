# CrocLens Database Schema

## Current Status

Phase 4 implements the first database schema foundation.

Implemented files:

- `apps/api/app/models/entities.py`
- `apps/api/app/db/base.py`
- `apps/api/app/db/session.py`
- `apps/api/alembic.ini`
- `apps/api/alembic/versions/20260505_0001_initial_schema.py`

No live PostgreSQL instance is required yet. The schema and migration are ready for a future PostgreSQL database.

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

Phase 4 implements all planned tables listed below.

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

Alembic:

- The migration tool used to apply versioned schema changes.

SQLAlchemy model:

- A Python class that maps to a database table.

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

## Relationship Map

```text
users
  -> user_profiles
  -> portfolios
      -> holdings
          -> tax_lots
      -> assets
          -> market_prices
          -> asset_scores
  -> liabilities
  -> real_estate_properties
  -> retirement_accounts
  -> decision_journal_entries
  -> action_plans
  -> agent_outputs
  -> watchlist_items
      -> assets

news_articles are stored separately and can be linked later by symbols or impact analysis.
```

## Design Choices

### One Assets Table

CrocLens uses one `assets` table for common asset metadata.

Why:

- Stocks, ETFs, mutual funds, crypto, bonds, and cash all need names, symbols, types, and source metadata.
- A shared table makes cross-asset comparison easier.

Tradeoff:

- Some asset types need extra fields. Those can be added in specialized tables later.

### Separate Holdings and Assets

`assets` describes what something is.

`holdings` describes what a user owns.

Example:

- Asset: VOO, Vanguard S&P 500 ETF
- Holding: Maya owns 20 shares of VOO in her taxable account

### Liabilities Are Separate

Liabilities are not assets with negative values.

Why:

- Debt needs fields like interest rate, minimum payment, and due day.
- Treating debt separately makes payoff planning easier.

### Agent Outputs Are Stored

AI outputs are stored in `agent_outputs`.

Why:

- We need to audit what the AI said.
- We need confidence, limitations, sources, and safety status.
- Future evaluation metrics can inspect stored outputs.

### Scores Are Versioned by Date

`asset_scores` stores score date and methodology version.

Why:

- Scoring formulas will change as the product improves.
- We need to know which formula produced a score.

## Index Strategy

Indexes were added where queries are likely:

- User lookup by email
- Portfolio lookup by user
- Holdings by portfolio and asset
- Assets by type and symbol
- Market prices by asset and date
- Decision journal entries by review date
- Agent outputs by user and agent
- Watchlist items by user

Indexes make reads faster but slow writes slightly. For MVP, we only add indexes that match obvious access patterns.

## Migration Strategy

Phase 4 adds one initial Alembic migration:

```text
20260505_0001_initial_schema.py
```

Later phases should add new migration files instead of editing this migration after it has been merged.

To run migrations later:

```bash
alembic -c apps/api/alembic.ini upgrade head
```

## PostgreSQL Notes

The Phase 4 model uses string UUID-style primary keys for MVP portability.

Production PostgreSQL could later use native `UUID` columns. That is a good improvement once the local development database setup is stable.
