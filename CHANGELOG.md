# Changelog

All notable CrocLens changes will be recorded here.

This project follows a phase-based learning and build workflow. Each phase should leave the repository in a clear, reviewable state.

## [Unreleased]

### Added

- Established Phase 0 product and system design foundation.
- Added project README with product vision, MVP strategy, tech stack, safety principles, and Git workflow.
- Added architecture, roadmap, data source, security, AI agent, database, API, AWS, evaluation, and learning documentation.
- Added Phase 1 static Next.js dashboard under `apps/web`.
- Added dark emerald sidebar, dashboard header, portfolio chart, allocation card, market snapshot, action plan card, tax insight, retirement progress, risk meter, and Croc Guide assistant panel.
- Added typed mock dashboard data and frontend utility formatters.
- Refined Phase 1 dashboard layout so Croc Guide opens as a side drawer from the Ask CrocLens button instead of taking permanent dashboard space.
- Added Phase 2 frontend routes for Dashboard, Portfolio, Compare Assets, Watchlist, Action Plans, Journal, Retirement, Tax Planner, and Settings.
- Added shared app shell for sidebar, main content, and Croc Guide drawer.
- Added placeholder page configuration and beginner-friendly placeholder content for future vertical slices.
- Added Phase 3 FastAPI backend skeleton under `apps/api`.
- Added health, portfolio summary, assets, action plan, and AI assistant mock endpoints.
- Added Pydantic request/response schemas, mock service layer, CORS setup for local frontend development, and backend API smoke tests.
- Added Phase 4 SQLAlchemy database models for cross-asset wealth tracking.
- Added Alembic initial migration for users, profiles, portfolios, holdings, assets, liabilities, real estate, retirement accounts, journal entries, action plans, agent outputs, market prices, news articles, watchlist items, tax lots, and asset scores.
- Added schema tests and expanded database documentation.
- Added Phase 5 frontend API client and dashboard data hook.
- Connected dashboard portfolio summary, tracked assets, and action plan cards to FastAPI mock endpoints.
- Added frontend loading, connected, and error states for backend API data.
- Added Phase 6 transparent portfolio and cross-asset calculation service.
- Added calculated net worth, total assets, total liabilities, allocation, debt impact, and cross-asset score formulas.
- Added backend calculation tests and dashboard scorecard rendering from API data.
- Added portfolio calculation documentation.
- Added Phase 7 API-backed beginner asset detail pages for stocks/ETFs, crypto, real estate, debt, and retirement.
- Added asset detail card and detail response contracts with confidence, limitations, source freshness, and safe next-step wording.
- Replaced the Portfolio placeholder with a detail-ready item index and linked dashboard comparison cards to detail pages.
- Added Phase 8 onboarding and risk profile flow.
- Added onboarding API contracts, risk scoring service, and backend tests.
- Added onboarding route, sidebar link, guided form, manual asset entry, and generated profile results.
- Added Phase 9 AI assistant v1 rule-based intent routing and safety checks.
- Added LLM-ready assistant prompt context structure and prompt versioning.
- Connected the Croc Guide drawer to the assistant API with loading, error, and structured answer states.
- Added Phase 10 lightweight multi-agent orchestrator and agent registry endpoint.
- Added assistant agent trace steps for intent routing, specialist handling, action planning, and safety review.
- Updated Croc Guide to show the agent trace behind each assistant answer.
- Added Phase 11 market data ingestion pipeline with sample JSON data.
- Added data provider registry, freshness report, lineage metadata, and basic data quality checks.
- Added data pipeline API routes, tests, and documentation.
- Removed ambiguous crypto provider integration so the MVP remains strictly free-only and sample-data driven by default.
- Added Phase 12 market news impact workflow with sample headlines mapped to affected holdings.
- Added `/market-news` frontend page, sidebar link, API route, tests, and documentation.
- Added Phase 13 tax-aware module with sample tax lots, unrealized gain/loss, holding-period labels, and wash-sale warning language.
- Replaced the Tax Planner placeholder with an API-backed educational tax insights page.
- Added Phase 14 retirement planner with sample retirement accounts, employer match explanation, contribution scenarios, tests, and documentation.
- Replaced the Retirement placeholder with an API-backed planner page.
- Added Phase 15 decision journal workflow with sample entries, entry creation, rule-based feedback, tests, and documentation.
- Replaced the Journal placeholder with an API-backed journal page.

### Notes

- The backend uses static mock data only.
- Database persistence is not implemented yet.
- A live PostgreSQL database is not required yet; Phase 4 defines the schema and migration foundation.
- Market snapshot and chart history still use sample frontend data until later data-pipeline phases.
- Phase 6 scores are educational heuristics and are intentionally simple for auditability.
- Phase 7 detail pages use static sample data and educational explanations, not personalized advice.
- Phase 8 risk profiles are educational starting points, not personalized investment recommendations.
- Phase 9 assistant responses are rule-based and educational; no external LLM is called yet.
- Phase 10 agent orchestration is deterministic; LangGraph or model-backed nodes can be introduced later.
- Phase 11 market data uses a local sample file by default; no live paid or ambiguous market data provider is connected.
