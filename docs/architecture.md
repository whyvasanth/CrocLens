# CrocLens Architecture

## Purpose

This document explains how CrocLens should be structured so the product can grow from a simple MVP into a production-quality AI wealth intelligence platform.

The main architecture goal is separation of concerns: each part of the system should have a clear job.

## High-Level System

```text
User
  |
  v
Next.js Web App
  |
  v
FastAPI REST API
  |
  +--> Portfolio and scoring services
  +--> AI assistant and agent orchestration
  +--> Data access layer
  |
  v
PostgreSQL

External data jobs, added later:
  SEC EDGAR
  FRED
  CoinGecko
  Treasury/Fiscal Data
  FHFA
  Alpha Vantage or similar free-tier market API
```

## Main System Boundaries

### Frontend

The frontend is responsible for presentation and user interaction.

It should:

- Render dashboard pages and forms.
- Show beginner-friendly explanations.
- Display charts, cards, and assistant responses.
- Call backend APIs through a clean API client layer.
- Handle loading, empty, and error states.

It should not:

- Own financial calculation rules.
- Talk directly to the database.
- Hide financial safety logic only in the browser.

### Backend

The backend is responsible for application behavior and data contracts.

It should:

- Expose REST endpoints.
- Validate request and response data with Pydantic.
- Run portfolio, scoring, and action-plan logic.
- Store and retrieve data through database models.
- Call AI orchestration code.
- Enforce safety rules before returning AI outputs.

### Database

The database is responsible for durable product data.

It should store:

- Users and profiles.
- Portfolios, holdings, assets, liabilities, and real estate.
- Retirement accounts and tax lots.
- Watchlist items and journal entries.
- AI outputs with confidence, limitations, and source metadata.
- Market prices and news articles.

### AI Layer

The AI layer is responsible for explaining and reasoning over user data in a safe educational way.

It starts simple:

```text
User question -> rule-based mock response -> safety wrapper -> API response
```

It grows later:

```text
User question
  -> Intent Router Agent
  -> Specialist Agent
  -> Safety/Compliance Guardrail Agent
  -> Structured AI response
```

### Data Engineering Layer

The data layer is responsible for getting external data into a useful, traceable format.

It should eventually handle:

- Extract: get data from public APIs or files.
- Transform: clean and normalize symbols, dates, prices, and source fields.
- Load: save normalized records into PostgreSQL.
- Freshness: show users when data was last updated.
- Quality checks: detect missing prices, duplicate records, and stale sources.

## Monorepo Decision

CrocLens will use a monorepo during the MVP.

Chosen structure:

```text
apps/web
apps/api
packages/shared
docs
```

Why this is the right MVP choice:

- One repository is easier for a solo builder to understand.
- Frontend, backend, docs, and shared contracts can evolve together.
- Pull requests can show a complete vertical slice.
- It avoids premature infrastructure complexity.

Tradeoff:

- Large companies may split services into separate repositories when ownership and deployment boundaries become complex.
- CrocLens does not need that complexity yet.

## Vertical Slice Architecture

Each major feature should move through the full stack.

Example: "Portfolio Overview"

```text
UI card
  -> GET /portfolio/summary
  -> portfolio calculation service
  -> holdings and liabilities tables
  -> tests for calculation correctness
  -> docs explaining formulas
```

This prevents disconnected UI mockups, isolated backend endpoints, or database tables that no feature uses.

## MVP Scope

The earliest useful MVP should include:

- Static dashboard using mock data.
- FastAPI backend with mock portfolio and AI endpoints.
- Database schema for cross-asset wealth.
- API integration between frontend and backend.
- Transparent portfolio and risk scoring logic.
- Safe mock AI assistant responses.

Not in the earliest MVP:

- Real brokerage integrations.
- Paid market data.
- Real trading.
- Full tax filing logic.
- Personalized financial advice.
- Complex real-time streaming architecture.

## Production Direction

Later production architecture can look like this:

```text
CloudFront/S3 or Amplify
  -> Next.js frontend

API Gateway
  -> Lambda running FastAPI with Mangum
  -> PostgreSQL
  -> SSM Parameter Store for secrets
  -> CloudWatch logs and metrics

Scheduled jobs
  -> market/news data ingestion
  -> database updates
  -> freshness checks
```

## Key Engineering Principles

- Keep calculations transparent and testable.
- Keep AI outputs structured and safety-checked.
- Store source and freshness metadata for external data.
- Prefer simple REST APIs before more complex event-driven systems.
- Use mock data first, then replace it with real data behind stable interfaces.
- Avoid paid data and expensive cloud services in the MVP.

