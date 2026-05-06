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
| SEC EDGAR | Company filings | Free, official, filing-focused |
| FRED | Macroeconomic data | Free API key, strong macro coverage |
| CoinGecko | Crypto prices and metadata | Free tier available, rate limits apply |
| Treasury/Fiscal Data | Treasury rates and public debt data | Free government source |
| FHFA | Housing price index data | Useful for real estate context |
| OpenFIGI | Symbol and security mapping | Free tier, useful for identifiers |
| Alpha Vantage or similar | Stocks and ETFs | Free tier often rate-limited |

Phase 11 adds the first optional free API integration:

```text
GET /api/v1/data-pipeline/crypto/bitcoin/live-preview
```

This endpoint calls CoinGecko's public simple price API when requested. It is intentionally optional and not required for tests because free public APIs can fail, rate limit, or change response timing.

### Stage 4: Optional Paid Providers

Paid providers should be clearly marked optional.

Possible future categories:

- Real-time equity market data
- Institutional fundamentals
- News sentiment APIs
- Broker aggregation
- Real estate valuation APIs

CrocLens MVP should not require paid providers.

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
