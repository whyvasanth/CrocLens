# Phase 11: Data Engineering Pipeline

## What We Built

Phase 11 adds the first CrocLens market data ingestion slice.

The backend now has:

- A local sample market data JSON fixture.
- A Pydantic-validated ingestion service.
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
Sample JSON file
      |
      v
Extract: read local file
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

## ETL Concepts

Extract:

- Pull raw data from a source.
- In Phase 11, the source is a local JSON file.
- No live crypto provider is connected in the MVP because the project is staying strictly free-only.

Transform:

- Convert raw provider data into CrocLens' internal shape.
- Example: a sample JSON record becomes a `MarketObservation` with symbol, value, source, and limitations.

Load:

- Save or expose normalized records.
- In Phase 11, records are returned through the API.
- Later, records should be written to PostgreSQL tables such as `market_prices`.

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
GET /api/v1/data-providers/status
```

Phase 21A added the normalized provider foundation. Phase 21B adds live-capable provider adapters for yfinance, CoinGecko public endpoints, FRED public CSV, Treasury/Fiscal Data, and SEC EDGAR.

The automated tests still do not make live network calls. They mock provider clients and verify normalization, source labels, cache behavior, and error contracts.

Crypto and market data remain sample-only in the main dashboard until persistence and live market API endpoints are added. Provider failures must produce unavailable or stale states, never hidden sample fallbacks.

## Provider Foundation

New package:

```text
apps/api/app/providers/
```

Key files:

- `models.py`: normalized quote, history, profile, filing, economic observation, and provider status models.
- `exceptions.py`: typed provider failures such as timeout, rate limit, invalid symbol, malformed response, and unavailable provider.
- `base.py`: shared provider runtime config, capability declarations, status reporting, and safe `asyncio.to_thread` helper for synchronous libraries.
- `registry.py`: capability routing and provider status aggregation.
- `cache.py`: small in-memory TTL cache that prevents repeated identical free-provider calls inside one process.
- `yfinance_provider.py`: quote, history, profile, dividend, and split adapter.
- `coingecko_provider.py`: no-key public crypto price/history adapter.
- `fred_provider.py`: no-key public CSV macro observation adapter.
- `treasury_provider.py`: official Fiscal Data rate context adapter.
- `sec_provider.py`: SEC ticker resolution and recent filings adapter gated by User-Agent configuration.

Why this matters:

- FastAPI routes should not import vendor clients directly.
- Provider failures need normalized metadata.
- Later stale-cache behavior needs a consistent result shape before persistence is added.
- Tests can mock the registry without relying on internet access.

## Production Upgrade Path

Later phases should add:

- Database persistence into `market_prices`.
- Scheduled ingestion jobs.
- Provider-specific retry logic.
- Provider response caching.
- Durable stale-while-revalidate storage.
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
