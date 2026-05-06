# CrocLens

See your money clearly.

CrocLens is a beginner-first AI wealth intelligence platform that helps people understand their full financial life across assets, liabilities, retirement, taxes, market context, and personal goals.

The product is designed to feel like a friendly AI-powered personal CFO for beginners: calm, premium, trustworthy, and simple enough that a new investor can understand what is happening.

Important safety note: CrocLens is educational software, not a licensed financial advisor. The product should never tell users to buy or sell specific investments, promise returns, or present personalized financial advice as certainty.

## Product Vision

CrocLens helps users answer beginner-friendly wealth questions:

- What do I own?
- What do I owe?
- How diversified am I?
- How risky is my overall financial picture?
- How do taxes, retirement, debt, and market news affect me?
- What should I consider reviewing next?

The AI assistant, Croc Guide, explains portfolio and money concepts in plain language, includes confidence and data limitations, and uses safe educational wording.

## MVP Strategy

We will not build every feature at once. CrocLens will be built in vertical slices.

A vertical slice means each meaningful feature should eventually include:

- Frontend UI
- Backend API
- Database model
- Business logic
- AI or agent logic when relevant
- Tests
- Documentation
- GitHub commit and pull request

The first MVP slices focus on a clean dashboard, mock portfolio data, a FastAPI backend, database schema, transparent portfolio calculations, and a safe mock AI assistant.

## Planned Tech Stack

Frontend:

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui when useful
- Recharts
- Lucide icons

Backend:

- FastAPI
- Python
- Pydantic
- SQLAlchemy or SQLModel
- PostgreSQL
- Alembic migrations when the database phase begins

AI layer:

- Mock AI responses first
- LLM-ready prompt structures next
- LangGraph-style multi-agent architecture later
- Safety and compliance guardrails around every AI output

Data layer:

- Manual user entry first
- Mock/sample data first
- Free public data sources next
- Paid providers marked as optional only

Deployment target:

- Low-cost AWS-compatible architecture
- Frontend on S3 + CloudFront or Amplify
- FastAPI on Lambda + API Gateway with Mangum, or a small low-cost service
- PostgreSQL through RDS only when budget allows, otherwise free external Postgres for MVP
- CloudWatch, AWS Budgets, and cost controls

## Future Repository Structure

The project will use a monorepo so the frontend, backend, docs, and shared contracts stay together while the product is small.

```text
CrocLens/
  apps/
    web/                 # Next.js frontend, created in Phase 1
    api/                 # FastAPI backend, created in Phase 3
  packages/
    shared/              # Shared schemas/types later if useful
  docs/
    architecture.md
    roadmap.md
    data-sources.md
    security.md
    ai-agents.md
    database-schema.md
    api-endpoints.md
    aws-deployment.md
    evaluation-metrics.md
    learning-notes.md
  CHANGELOG.md
  README.md
```

## Phase Roadmap

Completed phases:

- Phase 0: Product and system design foundation
- Phase 1: Static frontend dashboard
- Phase 2: Frontend pages and navigation
- Phase 3: Backend API skeleton
- Phase 4: Database schema
- Phase 5: Frontend-backend integration
- Phase 6: Portfolio and cross-asset logic
- Phase 7: Asset detail pages
- Phase 8: User onboarding and risk profile
- Phase 9: AI Assistant v1
- Phase 10: Multi-agent architecture
- Phase 11: Data engineering pipeline

Current phase:

- Phase 12: Market, news, and personal impact

Next phases:

- Phase 12 and beyond: Market/news impact, tax, retirement, journal, security, testing, metrics, and deployment

See [docs/roadmap.md](docs/roadmap.md) for the full plan.

## Financial Safety Principles

CrocLens AI outputs must include:

- Educational framing
- Confidence level
- Data limitations
- Source or freshness labels when available
- Safe wording
- No direct trading instructions
- No guaranteed returns

Preferred wording:

- "Consider reviewing..."
- "You may want to research..."
- "This could be a risk..."
- "Based on the data provided..."
- "This is educational, not financial advice."

Avoid wording:

- "Buy this stock"
- "Sell this now"
- "This will make money"
- "Guaranteed return"
- "This is the best investment"

## Local Status

Phase 1 and Phase 2 added the first runnable frontend app under `apps/web`.
Phase 3 adds the first runnable backend API under `apps/api`.
Phase 4 adds the SQLAlchemy database models and Alembic migration foundation.
Phase 5 connects the dashboard to the FastAPI mock API.
Phase 6 adds transparent portfolio and cross-asset scoring logic.
Phase 7 adds API-backed beginner detail pages for stocks/ETFs, crypto, real estate, debt, and retirement accounts.
Phase 8 adds an API-backed onboarding flow that turns goals, risk comfort, retirement, debt, and manual assets into a beginner risk profile.
Phase 9 connects Croc Guide to the assistant API with rule-based intent routing, prompt context, and safety checks.
Phase 10 adds a lightweight multi-agent orchestrator and visible agent trace for Croc Guide responses.
Phase 11 adds a sample market data ingestion pipeline, data quality checks, freshness metadata, and a free-only provider registry.
Phase 12 adds a market news impact workflow that maps sample headlines to affected holdings with safe educational wording.
Phase 13 adds an educational tax-aware module with sample tax lots, unrealized gain/loss, holding-period labels, and wash-sale warning language.
Phase 14 adds a retirement planner with sample accounts, employer match explanation, and contribution scenarios.
Phase 15 adds a decision journal workflow with sample entries, entry creation, and rule-based feedback.
Phase 16 adds watchlist intelligence with sample items, AI-style summaries, and safe risk/opportunity notes.
Phase 17 adds security headers, request IDs, rate limiting, prompt-injection checks, privacy controls, export/delete previews, and an API-backed Settings page.

Install dependencies:

```bash
npm install
```

Run the web app:

```bash
npm run dev:web
```

Open:

```text
http://localhost:3000/dashboard
```

The dashboard fetches portfolio summary, assets, and action plan data from the backend API. Market snapshot and chart history still use sample frontend data until later data-pipeline phases.

Optional frontend API override:

```bash
set NEXT_PUBLIC_CROCLENS_API_URL=http://127.0.0.1:8000
```

Current frontend routes:

- `/dashboard`
- `/onboarding`
- `/portfolio`
- `/compare-assets`
- `/market-news`
- `/watchlist`
- `/action-plans`
- `/journal`
- `/retirement`
- `/tax-planner`
- `/settings`
- `/assets/asset_stock_bucket`
- `/assets/asset_etf_bucket`
- `/assets/asset_btc`
- `/assets/asset_real_estate`
- `/assets/liability_mortgage`
- `/assets/asset_retirement`

Run the API:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r apps/api/requirements.txt
python -m uvicorn app.main:app --reload --app-dir apps/api --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

Current backend endpoints:

- `GET /health`
- `GET /api/v1/portfolio/summary`
- `GET /api/v1/assets`
- `GET /api/v1/assets/{asset_id}`
- `GET /api/v1/assets/detail-cards`
- `GET /api/v1/assets/{asset_id}/detail`
- `GET /api/v1/onboarding/options`
- `POST /api/v1/onboarding/profile`
- `GET /api/v1/ai/agents`
- `GET /api/v1/action-plans`
- `POST /api/v1/action-plans/generate`
- `POST /api/v1/ai/assistant`
- `GET /api/v1/data-pipeline/providers`
- `POST /api/v1/data-pipeline/market-data/sample-ingest`
- `GET /api/v1/data-pipeline/market-data/latest`
- `GET /api/v1/market-news/impact-summary`
- `GET /api/v1/tax/insights`
- `GET /api/v1/retirement/plan`
- `GET /api/v1/journal/entries`
- `POST /api/v1/journal/entries`
- `GET /api/v1/watchlist`
- `POST /api/v1/watchlist`
- `GET /api/v1/security/status`
- `GET /api/v1/privacy/settings`
- `PUT /api/v1/privacy/settings`
- `GET /api/v1/privacy/export`
- `DELETE /api/v1/privacy/data`

Assistant v1 supports:

- Rule-based intent routing
- Multi-agent trace steps
- Safe response wording
- Prompt context shape for future LLM calls
- Safety checks for direct trading or guaranteed-return language
- Confidence, data limitations, sources, and disclaimer fields

Database schema:

```text
apps/api/app/models/entities.py
apps/api/alembic/versions/20260505_0001_initial_schema.py
```

Run schema-related tests:

```bash
.venv\Scripts\python.exe -m pytest apps/api
```

Portfolio calculation docs:

```text
docs/portfolio-calculations.md
```

Data pipeline docs:

```text
docs/data-pipeline.md
```

## Git Workflow

Branch strategy:

- `main`
- `phase-0-product-system-design`
- `phase-1-static-dashboard`
- `phase-2-frontend-pages-navigation`
- `phase-3-backend-api`
- `phase-4-database-schema`
- `phase-5-frontend-backend-integration`
- `phase-6-cross-asset-logic`
- `phase-7-asset-detail-pages`
- `phase-8-onboarding-risk-profile`
- `phase-9-ai-assistant-v1`
- `phase-10-multi-agent-architecture`
- `phase-11-data-pipeline`
- `phase-12-market-news-impact`
- `phase-13-tax-aware-module`
- `phase-14-retirement-planner`
- `phase-15-decision-journal`
- `phase-16-watchlist-intelligence`
- `phase-17-security-reliability`
- `phase-18-testing`
- `phase-19-evaluation-metrics`
- `phase-20-deployment-plan`

Each phase should end with one branch, one clean commit, and one pull request.
