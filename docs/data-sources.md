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

### Current Real-Data Slice: Treasury Yield Curve

CrocLens now has a first real-data slice that uses the official U.S. Treasury public XML feed for Daily Treasury Par Yield Curve Rates:

```text
https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value={year}
```

Implemented records:

- 3-month Treasury yield
- 2-year Treasury yield
- 10-year Treasury yield
- 30-year Treasury yield

Why this source was chosen first:

- It is an official public government source.
- It does not require an API key.
- It does not require a paid subscription, free trial, credit card, or ambiguous freemium account.
- It is useful beginner context because Treasury yields affect cash yields, bonds, mortgages, and discount-rate discussions.

Important limitation:

- Treasury rates are macro context only. They do not provide live stock, ETF, mutual fund, or crypto prices.
- The dashboard should label Treasury values as real public data and keep unresolved stock/crypto data as sample/manual.

### Stage 3: Free Public APIs

Candidate sources:

| Source | Use | Notes |
| --- | --- | --- |
| SEC EDGAR | Company filings | Free, official, filing-focused |
| FRED | Macroeconomic data | Free API key, strong macro coverage |
| Treasury/Fiscal Data | Treasury rates and public debt data | First real-data slice implemented through the no-key public Treasury XML feed |
| FHFA | Housing price index data | Useful for real estate context |
| OpenFIGI | Symbol and security mapping | Free tier, useful for identifiers |

Current free-only policy:

- Use local sample files first.
- Prefer official public/government sources when real ingestion starts.
- Do not add ambiguous freemium or paid market data providers to the MVP.
- Keep crypto prices sample/manual until a verified no-cost source is selected.
- Do not add CoinGecko, Alpha Vantage, or similar providers unless we explicitly verify that the selected endpoint is truly free for the planned use and has acceptable terms.

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
