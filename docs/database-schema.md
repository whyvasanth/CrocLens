# CrocLens Database Schema

## Current Status

Phase 4 implemented the first database schema foundation. The production-MVP slices now use the schema for local persisted auth and user-owned portfolio holdings/liabilities.

Implemented files:

- `apps/api/app/models/entities.py`
- `apps/api/app/db/base.py`
- `apps/api/app/db/session.py`
- `apps/api/alembic.ini`
- `apps/api/alembic/versions/20260505_0001_initial_schema.py`

Local Docker now runs PostgreSQL for development. Backend tests may still use SQLite for speed, but Alembic migrations and Docker are the source of truth for runtime behavior.

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

Current implementation:

- `POST /api/v1/portfolio/holdings` creates manual holdings for the authenticated user.
- Signup manual assets are persisted as holdings.
- Portfolio summary calculations aggregate holdings by asset type.
- Ownership is enforced through `portfolios.user_id`.

### liabilities

Stores what the user owes.

Examples:

- Mortgage
- Student loan
- Credit card debt
- Personal loan

Current implementation:

- `POST /api/v1/portfolio/liabilities` creates manual debts for the authenticated user.
- Liabilities reduce net worth in `/api/v1/portfolio/summary`.
- Ownership is enforced through `liabilities.user_id`.

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
- `provider_ingestion_runs`
- `provider_errors`
- `portfolio_net_worth_snapshots`
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
      -> portfolio_net_worth_snapshots
  -> provider_errors
      -> assets
  -> liabilities
  -> real_estate_properties
  -> retirement_accounts
  -> decision_journal_entries
  -> action_plans
  -> agent_outputs
  -> watchlist_items
      -> assets

news_articles are stored separately and can be linked later by symbols or impact analysis.

provider_ingestion_runs track scheduled or manual provider refresh jobs.
```

## Market Observation Cache

Phase 21C expands `market_prices` from a basic price table into a provider-aware observation cache.

Each stored market observation includes:

- `asset_id`
- `price_date`
- `close_price`
- `currency`
- `source_name`
- `provider_status`
- `data_quality`
- `data_as_of`
- `retrieved_at`
- `is_stale`
- `is_sample_data`
- `source_url`
- `data_limitations`
- optional `raw_response_metadata`

The uniqueness rule remains:

```text
asset_id + price_date + source_name
```

That prevents duplicate daily observations from the same provider while still allowing multiple providers later.

## Provider Runs And Errors

`provider_ingestion_runs` records every refresh attempt:

- provider
- operation
- status
- started and completed timestamps
- requested, accepted, and rejected counts
- error summary when a run fails

`provider_errors` records normalized provider failures:

- provider
- operation
- asset or symbol
- error code
- error message
- retryability

This matters because provider failure must not silently become sample data.

## Net Worth Snapshots

`portfolio_net_worth_snapshots` stores one snapshot per portfolio per day.

It captures:

- total assets
- total liabilities
- net worth
- source name
- data quality

The table supports future portfolio history charts without inventing trend lines.

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

## Runtime Persistence Notes

The Next.js frontend does not read the local auth token directly. It calls `/api/backend/api/v1/...`, and the BFF route forwards the HttpOnly cookie token to FastAPI. That lets authenticated portfolio endpoints use PostgreSQL without exposing session tokens to browser JavaScript.

Current persisted areas:

- Local users and bcrypt password hashes.
- Local auth sessions.
- Default user portfolios.
- Manual holdings.
- Manual liabilities.

Still sample-backed:

- Market prices and chart history.
- Tax lots.
- Retirement plans.
- Market news.
- Watchlist intelligence.
- Decision journal entries.
