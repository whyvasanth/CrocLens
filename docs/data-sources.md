# CrocLens Data Sources

## Data Strategy

CrocLens will start with manual entry and mock data. This is intentional.

Beginners need a reliable product experience before the system depends on external data providers. Mock data lets us design the UI, API contracts, database schema, calculations, and AI safety patterns without being blocked by API keys or rate limits.

## Data Source Stages

## Phase 21 Provider Layer

Phase 21 adds a vendor-agnostic provider registry inspired by TradingAgents' routing pattern, but redesigned for CrocLens' beginner wealth intelligence use case.

Provider rules:

- CrocLens stays runnable without API keys.
- Live providers are optional and must fall back to sample data.
- Every provider response includes source, freshness, confidence, retrieved time, and limitations.
- Agents and API routes use normalized provider objects instead of raw vendor payloads.
- Paid APIs and ambiguous free trials remain out of scope.

Implemented or scaffolded providers:

| Provider | Use | Status |
| --- | --- | --- |
| yfinance | Stock/ETF prototype price and history | Implemented, unofficial, fallback-safe |
| stockstats | Technical indicators from OHLCV | Implemented as derived indicator layer |
| CoinGecko | Crypto price context | Implemented with public/demo endpoint and fallback |
| FRED | Macro series | Implemented only when `FRED_API_KEY` exists |
| Treasury Fiscal Data | Treasury/rate context | Implemented as optional endpoint, not wired into dashboard |
| Alpha Vantage | Stock/ETF backup | Documented stub |
| SEC EDGAR | Filings and fundamentals | Documented stub |
| FHFA | Housing index context | Documented stub |
| Census | Local real estate/economic context | Documented stub |
| OpenFIGI | Identifier mapping | Documented stub |

Default mode:

```text
DATA_PROVIDER_MODE=mock_or_live
```

If a provider is missing, unconfigured, rate-limited, or unavailable, CrocLens returns deterministic sample fallback data with explicit limitations.

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
| SEC EDGAR | Company filings | Free, official, filing-focused |
| FRED | Macroeconomic data | Free API key, strong macro coverage |
| Treasury/Fiscal Data | Treasury rates and public debt data | Free government source |
| FHFA | Housing price index data | Useful for real estate context |
| OpenFIGI | Symbol and security mapping | Free tier, useful for identifiers |

Current free-only policy:

- Use local sample files first.
- Prefer official public/government sources when real ingestion starts.
- Do not add ambiguous freemium or paid market data providers to the MVP.
- Keep crypto prices sample/manual by default; the optional CoinGecko public/demo path must fall back safely when rate-limited or unavailable.

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
