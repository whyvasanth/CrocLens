# Phase 11: Data Engineering Pipeline

## What We Built

Phase 11 added the first CrocLens market data ingestion shape. The current real-data update adds the first live public source: official U.S. Treasury yield curve data.

The backend now has:

- A local sample market data JSON fixture.
- A Pydantic-validated ingestion service.
- A live no-key Treasury yield curve ingestion service.
- Basic data quality checks.
- Freshness and lineage metadata.
- Data provider registry.
- Backend tests for the pipeline and API contracts.

This is not a full production data platform yet. It is the MVP shape that lets us learn ETL safely.

## Why This Matters

CrocLens cannot become a trustworthy wealth intelligence product unless users know where data came from, how fresh it is, and what its limitations are.

For a beginner finance app, stale or unclear data is dangerous because a user may overtrust it. That is why Phase 11 adds source labels, freshness labels, quality issues, confidence, and data limitations before live market data becomes central to the UI.

## Architecture

```text
Sample JSON file or Treasury public XML feed
      |
      v
Extract: read local file or fetch official Treasury XML
      |
      v
Transform: validate with Pydantic and normalize records
      |
      v
Quality checks: duplicates, zero values, missing limitations
      |
      v
Load for MVP: return API response from memory
      |
      v
Future load: persist to market_prices table
```

Current implementation:

```text
apps/api/data/sample_market_data.json
apps/api/app/services/data_pipeline.py
apps/api/app/api/routes/data_pipeline.py
```

Real-data v1 source:

```text
U.S. Treasury Daily Treasury Par Yield Curve Rates
https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve
```

The backend fetches the public XML feed for the current year, parses the latest and previous daily rows, normalizes selected maturities into `MarketObservation` records, and computes day-over-day yield movement in percentage points.

## ETL Concepts

Extract:

- Pull raw data from a source.
- In Phase 11, the source is a local JSON file.
- In real-data v1, the source is the official public Treasury XML feed.
- No live crypto provider is connected in the MVP because the project is staying strictly free-only.

Transform:

- Convert raw provider data into CrocLens' internal shape.
- Example: a sample JSON record becomes a `MarketObservation` with symbol, value, source, and limitations.

Load:

- Save or expose normalized records.
- In Phase 11, records are returned through the API.
- Later, records should be written to PostgreSQL tables such as `market_prices`.
- Real-data v1 still returns records from memory. Database persistence remains a later step.

## Data Quality Checks

The Phase 11 pipeline checks:

- Duplicate symbol, metric, and date combinations.
- Zero values that may need review.
- Missing data limitation notes.

Why this matters:

- Bad data can create bad AI output.
- Quality checks catch issues before they reach dashboards or agents.
- Tests make ingestion repeatable.

## Freshness And Lineage

Freshness tells users how current the data is.

Lineage tells users where the data came from.

Each market observation includes:

- `source.name`
- `source.freshness`
- `source.as_of`
- `retrieved_at`
- `source_url`
- `data_limitations`

## Implemented Endpoints

```http
GET /api/v1/data-pipeline/providers
POST /api/v1/data-pipeline/market-data/sample-ingest
GET /api/v1/data-pipeline/market-data/latest
POST /api/v1/data-pipeline/market-data/treasury-ingest
GET /api/v1/data-pipeline/market-data/treasury-latest
```

`treasury-latest` is the dashboard's first real market context endpoint. Stock, ETF, mutual fund, and crypto prices remain sample/manual until we choose verified no-cost sources with acceptable terms.

## Production Upgrade Path

Later phases should add:

- Database persistence into `market_prices`.
- Scheduled ingestion jobs.
- Provider-specific retry logic.
- Provider response caching.
- Rate-limit handling.
- Dead-letter storage for failed records.
- Data quality dashboards.
- More provider clients for FRED, Treasury/Fiscal Data, FHFA, SEC EDGAR, and OpenFIGI.
- A verified no-cost crypto source only if it fits the project budget and terms.

## Safety Notes

Market data endpoints should never imply a user should buy or sell.

They should support educational context only:

- "Based on the data available..."
- "This may be stale..."
- "Consider reviewing..."
- "This is educational, not financial advice."

## Mini Assignment

Add one new sample record for a bond ETF, such as `AGG`.

Then run:

```bash
.venv\Scripts\python.exe -m pytest apps/api
```

Check that:

- The ingestion count increases by one.
- The latest market data endpoint includes the new symbol.
- The record includes data limitations.
