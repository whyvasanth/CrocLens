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

Current phase:

- Phase 5: Frontend-backend integration

Next phases:

- Phase 6: Portfolio and cross-asset logic
- Phase 7 and beyond: Asset detail pages, onboarding, AI assistant, agents, data pipelines, security, testing, metrics, and deployment

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
- `/portfolio`
- `/compare-assets`
- `/watchlist`
- `/action-plans`
- `/journal`
- `/retirement`
- `/tax-planner`
- `/settings`

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
- `GET /api/v1/action-plans`
- `POST /api/v1/action-plans/generate`
- `POST /api/v1/ai/assistant`

Database schema:

```text
apps/api/app/models/entities.py
apps/api/alembic/versions/20260505_0001_initial_schema.py
```

Run schema-related tests:

```bash
.venv\Scripts\python.exe -m pytest apps/api
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
