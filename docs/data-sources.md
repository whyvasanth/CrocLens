# CrocLens Data Sources

## Data Strategy

CrocLens will start with manual entry and mock data. This is intentional.

Beginners need a reliable product experience before the system depends on external data providers. Mock data lets us design the UI, API contracts, database schema, calculations, and AI safety patterns without being blocked by API keys or rate limits.

## Data Source Stages

### Stage 1: Manual and Mock Data

Use for:

- Portfolio holdings
- Real estate properties
- Cash balances
- Retirement accounts
- Mortgages
- Student loans
- Credit card debt
- Decision journal entries

Benefits:

- No vendor dependency
- No paid API costs
- Easier testing
- Faster product iteration

Tradeoff:

- Users must enter data manually.
- Market prices may not be live.

### Stage 2: Sample Files

Use sample JSON or CSV files for:

- Market prices
- Asset metadata
- News examples
- Treasury rates

Phase 11 implements this stage with:

```text
apps/api/data/sample_market_data.json
```

The sample file is loaded by a tested FastAPI service that validates records, returns freshness metadata, and reports quality issues. This keeps the MVP deterministic while teaching the same ETL pattern used for real providers.

Benefits:

- Teaches data engineering basics.
- Supports repeatable tests.
- Avoids external failures during development.

### Stage 3: Free Public APIs

Candidate sources:

| Source | Use | Notes |
| --- | --- | --- |
| yfinance | Stocks, ETFs, indexes, historical prices, dividends, splits | No API key, unofficial Yahoo Finance wrapper, prototype/MVP only |
| CoinGecko public endpoints | Common crypto price context | No-key public endpoint path only, rate limited |
| SEC EDGAR | Company filings | Free, official, filing-focused |
| FRED public CSV | Macroeconomic data | No-key public CSV endpoints where available; observations may be revised |
| Treasury/Fiscal Data | Treasury rates and public debt data | Free government source |
| FHFA | Housing price index data | Useful for real estate context |
| OpenFIGI | Symbol and security mapping | Optional only if no-cost access and terms fit the MVP |

Current free-only policy:

- Use local sample files first.
- yfinance is the first stock/ETF/index MVP provider, but it must be labeled unofficial, delayed or incomplete, and educational only.
- Prefer official public/government sources for filings, macro, Treasury, and housing context.
- CoinGecko public no-key endpoints may be used only with rate-limit-aware caching and clear unavailability states.
- Do not add ambiguous freemium or paid market data providers to the MVP.

## Phase 21A Provider Foundation

Phase 21A adds a provider registry at:

```http
GET /api/v1/data-providers/status
```

The registry reports provider readiness, configuration, cache/stale settings, capabilities, and limitations for:

- `yfinance`
- `coingecko`
- `fred`
- `treasury`
- `sec_edgar`

This phase does not fetch live market data yet. It creates the contract that later phases will use.

Provider responses must eventually include:

- `provider_name`
- `provider_status`
- `data_as_of`
- `retrieved_at`
- `is_stale`
- `is_sample_data`
- `data_quality`
- `confidence`
- `source_url`
- `data_limitations`
- normalized error details when unavailable

Important rule:

- Provider failure must return cached/stale or unavailable data honestly.
- CrocLens must never silently relabel failed live provider data as sample data or fresh data.

### Stage 4: Disallowed For MVP

Paid providers are out of scope for this MVP.

Do not add these without an explicit future decision:

- Real-time equity market data
- Institutional fundamentals
- News sentiment APIs
- Broker aggregation
- Real estate valuation APIs

CrocLens MVP must not require paid providers, free trials that later bill, or ambiguous freemium APIs.

## Data Freshness

Every external data record should eventually include:

- `source_name`
- `source_url` when possible
- `as_of_date`
- `retrieved_at`
- `freshness_status`

Example labels:

- "Updated today"
- "Updated 2 days ago"
- "Sample data"
- "Manual entry"
- "Stale, review before relying on this"

## Data Quality Checks

Later ingestion jobs should check:

- Missing required fields
- Duplicate prices for the same symbol and date
- Negative prices where not valid
- Unknown symbols
- Stale records
- API rate limit failures
- Partial ingestion failures

Phase 11 currently checks:

- Duplicate symbol, metric, and date combinations
- Zero values that may need review
- Missing data limitation notes

See `docs/data-pipeline.md` for the Phase 11 pipeline design.

## Data Engineering Concepts

Extract:

- Pull data from an API, CSV, or JSON file.

Transform:

- Clean names, dates, symbols, and numeric fields.

Load:

- Save normalized records into the database.

Freshness:

- Track how current the data is.

Lineage:

- Track where data came from.

Caching:

- Store reused data to avoid unnecessary API calls.

Retries:

- Try again when temporary external failures happen.

Rate limits:

- Respect provider limits to avoid blocked requests or surprise costs.
