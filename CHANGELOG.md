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

### Notes

- The frontend uses static mock data only.
- The backend uses static mock data only.
- Database persistence is not implemented yet.
