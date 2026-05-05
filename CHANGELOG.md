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

### Notes

- The backend uses static mock data only.
- Database persistence is not implemented yet.
- A live PostgreSQL database is not required yet; Phase 4 defines the schema and migration foundation.
- Market snapshot and chart history still use sample frontend data until later data-pipeline phases.
- Phase 6 scores are educational heuristics and are intentionally simple for auditability.
- Phase 7 detail pages use static sample data and educational explanations, not personalized advice.
