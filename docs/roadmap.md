# CrocLens Roadmap

## Roadmap Strategy

CrocLens will be built in phases. Each phase should teach one major engineering idea and leave the repository in a useful state.

The build order intentionally starts with product architecture and mock data before real AI, real market data, or cloud deployment. This keeps the system understandable and reduces expensive mistakes.

## Phase 0: Product and System Design Foundation

Goal:

- Define product vision, MVP scope, architecture, safety rules, data strategy, and GitHub workflow.

Deliverables:

- README
- Architecture docs
- Roadmap docs
- Data source docs
- Security docs
- AI agent docs
- Changelog

Branch:

- `phase-0-product-system-design`

Commit:

- `docs: add CrocLens product and system design blueprint`

## Phase 1: Frontend Static Dashboard

Goal:

- Build a premium, beginner-friendly CrocLens dashboard in Next.js with mock data.

Status:

- Implemented in `apps/web` with static mock data.

Key UI:

- Dark emerald sidebar
- White and mint dashboard surface
- Portfolio overview chart
- Net worth and allocation cards
- Market snapshot
- Action plan
- Tax-aware insight
- Retirement progress
- Risk meter
- Croc Guide assistant panel

Branch:

- `phase-1-static-dashboard`

Commit:

- `feat: build static dashboard layout`

## Phase 2: Frontend Pages and Navigation

Goal:

- Add the main product routes and placeholder pages.

Status:

- Implemented with Next.js App Router pages, shared app shell, real sidebar links, and beginner-friendly placeholders.

Pages:

- Dashboard
- Portfolio
- Compare Assets
- Watchlist
- Action Plans
- Journal
- Retirement
- Tax Planner
- Settings

Branch:

- `phase-2-frontend-pages-navigation`

Commit:

- `feat: add frontend pages and navigation`

## Phase 3: Backend API Skeleton

Goal:

- Create the FastAPI backend with mock endpoints.

Status:

- Implemented under `apps/api` with FastAPI routers, Pydantic schemas, mock services, and smoke tests.

Endpoints:

- Health check
- Portfolio summary
- Assets
- Action plan
- AI assistant

Branch:

- `phase-3-backend-api`

Commit:

- `feat: add FastAPI backend skeleton`

## Phase 4: Database Design

Goal:

- Add the PostgreSQL schema that supports cross-asset wealth tracking.

Status:

- Implemented with SQLAlchemy models and an Alembic initial migration.

Tables:

- users
- user_profiles
- portfolios
- holdings
- assets
- liabilities
- real_estate_properties
- retirement_accounts
- decision_journal_entries
- action_plans
- agent_outputs
- market_prices
- news_articles
- watchlist_items
- tax_lots
- asset_scores

Branch:

- `phase-4-database-schema`

Commit:

- `feat: add cross-asset database schema`

## Phase 5: Frontend-Backend Integration

Goal:

- Replace frontend mock data with API calls.

Status:

- Implemented for dashboard portfolio summary, tracked assets, and action plan data using the FastAPI mock API.

Topics:

- API client layer
- Loading states
- Error states
- Data contracts

Branch:

- `phase-5-frontend-backend-integration`

Commit:

- `feat: connect dashboard to portfolio API`

## Phase 6: Portfolio and Cross-Asset Logic

Goal:

- Implement transparent wealth and risk calculations.

Status:

- Implemented as a tested backend calculation service and API-backed dashboard scorecard.

Calculations:

- Net worth
- Total assets
- Total liabilities
- Asset allocation
- Debt impact
- Risk score
- Liquidity score
- Diversification score
- Income/yield score
- Inflation sensitivity
- Tax complexity score

Branch:

- `phase-6-cross-asset-logic`

Commit:

- `feat: implement cross-asset scoring logic`

## Phase 7: Asset Detail Pages

Goal:

- Add beginner-friendly detail pages for major asset types.

Status:

- Implemented with API-backed detail cards, dynamic Next.js detail routes, beginner explanations, and backend tests.

Pages:

- Stock/ETF
- Crypto
- Real estate
- Debt/liability
- Retirement account

Branch:

- `phase-7-asset-detail-pages`

Commit:

- `feat: add asset detail pages`

## Phase 8: User Onboarding and Risk Profile

Goal:

- Collect user goals, experience, risk tolerance, time horizon, and manual assets.

Status:

- Implemented with an API-backed onboarding form, manual asset entry, heuristic risk profile scoring, safe first steps, and tests.

Branch:

- `phase-8-onboarding-risk-profile`

Commit:

- `feat: add onboarding and risk profile flow`

## Phase 9: AI Assistant v1

Goal:

- Add a simple safe assistant endpoint using rule-based or mock responses.

Status:

- Implemented with rule-based intent routing, LLM-ready prompt context, safety checks, Croc Guide frontend integration, and tests.

Branch:

- `phase-9-ai-assistant-v1`

Commit:

- `feat: add AI assistant mock response endpoint`

## Phase 10: Multi-Agent Architecture

Goal:

- Add agent routing and specialist agent skeletons.

Status:

- Implemented as a deterministic lightweight orchestrator with an agent registry, assistant trace steps, and Croc Guide trace rendering.

Branch:

- `phase-10-multi-agent-architecture`

Commit:

- `feat: add multi-agent orchestration skeleton`

## Phase 11: Data Engineering Pipeline

Goal:

- Add sample market data ingestion and a free-only provider plan.

Status:

- Implemented with a local sample market data fixture, Pydantic validation, freshness metadata, quality checks, provider registry, and tests. Live market providers remain unconnected until a verified no-cost source is selected.

Branch:

- `phase-11-data-pipeline`

Commit:

- `feat: add market data ingestion pipeline`

## Phase 12: Market, News, and Personal Impact

Goal:

- Build "How does this affect me?" analysis using holdings and news context.

Status:

- Implemented with sample news articles, affected holding mapping, safe suggested questions, an API endpoint, frontend page, tests, and documentation.

Branch:

- `phase-12-market-news-impact`

Commit:

- `feat: add market news impact workflow`

## Phase 13: Tax-Aware Module

Goal:

- Add tax lots, unrealized gain/loss, holding period explanations, and safe tax-language warnings.

Status:

- Implemented with sample tax lots, gain/loss calculations, short-term versus long-term labels, tax-loss harvesting education, wash-sale warning language, API tests, and an API-backed Tax Planner page.

Branch:

- `phase-13-tax-aware-module`

Commit:

- `feat: add tax-aware insight module`

## Phase 14: Retirement and 401(k) Planner

Goal:

- Track retirement accounts, contributions, employer match, and progress scenarios.

Status:

- Implemented with sample retirement accounts, employer match explanation, contribution scenarios, API tests, and an API-backed Retirement page.

Branch:

- `phase-14-retirement-planner`

Commit:

- `feat: add retirement planner workflow`

## Phase 15: Decision Journal and Feedback Loop

Goal:

- Let users record financial decisions and review outcomes later.

Status:

- Implemented with sample decision entries, entry creation, rule-based feedback, API tests, and an API-backed Journal page.

Branch:

- `phase-15-decision-journal`

Commit:

- `feat: add decision journal workflow`

## Phase 16: Watchlist Intelligence

Goal:

- Let users watch assets and track why each one matters.

Status:

- Implemented with sample watchlist items, preview item creation, educational AI-style summaries, risk notes, opportunity notes, API tests, and an API-backed Watchlist page.

Branch:

- `phase-16-watchlist-intelligence`

Commit:

- `feat: add watchlist intelligence`

## Phase 17: Security and Reliability

Goal:

- Add auth plan, validation, rate limiting, logging, error handling, privacy controls, export, and delete flows.

Branch:

- `phase-17-security-reliability`

Commit:

- `feat: add security and reliability foundation`

## Phase 18: Testing and CI

Goal:

- Add frontend tests, backend tests, API tests, calculation tests, agent output tests, and GitHub Actions.

Branch:

- `phase-18-testing`

Commit:

- `test: add portfolio calculation tests`

## Phase 19: Evaluation Metrics

Goal:

- Define metrics for product quality, AI safety, reliability, data freshness, and user learning.

Branch:

- `phase-19-evaluation-metrics`

Commit:

- `docs: add evaluation metrics plan`

## Phase 20: Deployment Plan

Goal:

- Dockerize services and document low-cost AWS deployment.

Branch:

- `phase-20-deployment-plan`

Commit:

- `docs: add AWS deployment and cost-control plan`
