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
- Verified no-cost public data sources only
- No paid, trial-based, or ambiguous freemium data providers

Deployment target:

- Local development first
- GitHub for source control and documentation
- Free-only deployment options may be evaluated later
- No AWS, paid cloud, paid auth, paid database, or paid data provider unless explicitly approved

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
- Phase 12: Market, news, and personal impact
- Phase 13: Tax-aware module
- Phase 14: Retirement planner
- Phase 15: Decision journal
- Phase 16: Watchlist intelligence
- Phase 17: Security and reliability
- Phase 18: Testing and CI
- Phase 19: Evaluation metrics
- Phase 20: Free-only deployment plan
- Phase 21A-21D: Market provider foundation, free provider adapters, persisted market observations, and live market/portfolio history APIs
- Phase 22: Public landing page, demo mode, dashboard product polish, and real market snapshot wiring
- Phase 23: User-specific persistence for planning and research workflows
- Phase 24: Grounded Croc Guide responses from saved user data
- Phase 25: Behavioral tests and automatic quality gates

Current status:

- MVP foundation complete through Phase 25

Next work:

- Prepare the cost-conscious AWS deployment files and runbook.

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
Phase 10 adds a lightweight multi-agent orchestrator, and Phase 24 keeps the user-facing guide focused on collapsed evidence instead of technical trace details.
Phase 11 adds a sample market data ingestion pipeline, data quality checks, freshness metadata, and a free-only provider registry.
Phase 12 adds a market news impact workflow that maps sample headlines to affected holdings with safe educational wording.
Phase 13 adds an educational tax-aware module with sample tax lots, unrealized gain/loss, holding-period labels, and wash-sale warning language.
Phase 14 adds a retirement planner with sample accounts, employer match explanation, and contribution scenarios.
Phase 15 adds a decision journal workflow with sample entries, entry creation, and rule-based feedback.
Phase 16 adds watchlist intelligence with sample items, AI-style summaries, and safe risk/opportunity notes.
Phase 17 adds security headers, request IDs, rate limiting, prompt-injection checks, privacy controls, export/delete previews, and an API-backed Settings page.
Phase 18 adds backend agent-output tests, frontend smoke tests, and a manual-only free-usage GitHub Actions CI workflow.
Phase 19 adds an internal evaluation metrics dashboard for product quality, AI safety, data freshness, and reliability.
Phase 20 adds local Docker deployment files and a free-only deployment plan that blocks AWS and paid cloud by default.
Phase 21A-21D add free-first market provider contracts, live-capable yfinance/public provider adapters, persisted market observations, and portfolio history endpoints.
Phase 22 adds a public landing page, explicit Demo Mode, grouped beginner navigation, endpoint-backed market snapshot data, account-aware net-worth history behavior, and friendlier signup validation.
Phase 23 persists watchlist items, decision journal entries, action plans, retirement accounts, tax lots, and privacy settings for authenticated users while keeping demo/sample fallbacks clearly labeled.
Phase 24 grounds Croc Guide in saved user records and provider freshness metadata, then returns observations, evidence, considerations, confidence, stale/sample flags, and educational disclaimers.
Phase 25 adds Vitest behavior tests, React Testing Library component tests, API-client BFF routing tests, Playwright smoke coverage, and automatic GitHub Actions quality gates.

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
http://localhost:3000
```

The public home page links to Demo Mode and account creation. The dashboard fetches portfolio summary, assets, action plan data, and market snapshot data from the backend API. Signed-in net-worth history uses stored snapshots when available; demo visitors see clearly labeled sample history.

Optional frontend API override:

```bash
set NEXT_PUBLIC_CROCLENS_API_URL=http://127.0.0.1:8000
```

Current frontend routes:

- `/`
- `/login`
- `/signup`
- `/dashboard`
- `/onboarding` redirects to `/signup`
- `/portfolio`
- `/compare-assets`
- `/market-news`
- `/watchlist`
- `/action-plans`
- `/journal`
- `/retirement`
- `/tax-planner`
- `/internal/evaluation-metrics`
- `/evaluation-metrics` redirects to `/internal/evaluation-metrics`
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
python -m alembic -c apps/api/alembic.ini upgrade head
python -m uvicorn app.main:app --reload --app-dir apps/api --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

Seed the local test user after PostgreSQL and migrations are running:

```bash
$env:PYTHONPATH="apps/api"
.venv\Scripts\python.exe -m app.scripts.seed_test_user
```

Default local test credentials:

```text
Email: test@croclens.local
Password: Test-user-123
```

Run both services with local Docker:

```bash
npm.cmd run docker:up
```

Open:

```text
http://localhost:3000/dashboard
http://127.0.0.1:8000/docs
```

Stop Docker services:

```bash
npm.cmd run docker:down
```

Seed the same test user in Docker:

```bash
docker compose exec api python -m app.scripts.seed_test_user
```

Current backend endpoints:

- `GET /health`
- `GET /api/v1/portfolio/summary`
- `GET /api/v1/assets`
- `GET /api/v1/assets/{asset_id}`
- `GET /api/v1/assets/detail-cards`
- `GET /api/v1/assets/{asset_id}/detail`
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `GET /api/v1/onboarding/options`
- `POST /api/v1/onboarding/profile`
- `GET /api/v1/ai/agents`
- `GET /api/v1/action-plans`
- `POST /api/v1/action-plans/generate`
- `POST /api/v1/action-plans/items/{item_id}/complete`
- `POST /api/v1/action-plans/items/{item_id}/dismiss`
- `POST /api/v1/action-plans/items/{item_id}/reopen`
- `POST /api/v1/ai/assistant`
- `GET /api/v1/data-pipeline/providers`
- `POST /api/v1/data-pipeline/market-data/sample-ingest`
- `GET /api/v1/data-pipeline/market-data/latest`
- `GET /api/v1/market-news/impact-summary`
- `GET /api/v1/tax/insights`
- `POST /api/v1/tax/lots`
- `PUT /api/v1/tax/lots/{lot_id}`
- `DELETE /api/v1/tax/lots/{lot_id}`
- `GET /api/v1/retirement/plan`
- `POST /api/v1/retirement/accounts`
- `PUT /api/v1/retirement/accounts/{account_id}`
- `DELETE /api/v1/retirement/accounts/{account_id}`
- `GET /api/v1/journal/entries`
- `POST /api/v1/journal/entries`
- `PUT /api/v1/journal/entries/{entry_id}`
- `DELETE /api/v1/journal/entries/{entry_id}`
- `GET /api/v1/watchlist`
- `POST /api/v1/watchlist`
- `PUT /api/v1/watchlist/{item_id}`
- `DELETE /api/v1/watchlist/{item_id}`
- `GET /api/v1/security/status`
- `GET /api/v1/privacy/settings`
- `PUT /api/v1/privacy/settings`
- `GET /api/v1/privacy/export`
- `DELETE /api/v1/privacy/data`
- `GET /api/v1/evaluation/metrics`

Assistant v1 supports:

- Rule-based intent routing
- Grounded context from authenticated user records
- Collapsed evidence and source details
- Safe response wording
- Prompt context shape for future LLM calls
- Safety checks that return safe categories instead of echoing unsafe wording
- Confidence, data limitations, sources, sample/stale flags, and disclaimer fields

Database schema:

```text
apps/api/app/models/entities.py
apps/api/alembic/versions/20260505_0001_initial_schema.py
```

Run schema-related tests:

```bash
.venv\Scripts\python.exe -m pytest apps/api
```

Run frontend checks:

```bash
npm.cmd run typecheck:web
npm.cmd run test:unit --workspace @croclens/web
npm.cmd run test:web
npm.cmd run build:web
npm.cmd audit --omit=dev
npm.cmd run test:e2e --workspace @croclens/web
```

CI:

```text
.github/workflows/ci.yml
```

The workflow runs on pull requests, pushes to `main`, and manual dispatch. Use GitHub Actions only when it stays within free or included usage for your repository/account.

Portfolio calculation docs:

```text
docs/portfolio-calculations.md
```

Data pipeline docs:

```text
docs/data-pipeline.md
```

Testing and CI docs:

```text
docs/testing-ci.md
```

Evaluation metrics docs:

```text
docs/evaluation-metrics.md
```

Free-only deployment docs:

```text
docs/aws-deployment.md
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
- `main` currently contains the completed local MVP phases because this repository is being built directly on main by request.

The original learning workflow used one branch per phase. This local MVP build is currently committing directly to `main` by request, so each phase should still keep one clean, reviewable commit.
