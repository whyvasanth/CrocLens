# Phase 18: Testing And CI

## What We Built

Phase 18 strengthens the CrocLens test strategy.

Backend:

- API contract tests.
- Portfolio calculation tests.
- Database schema tests.
- Data pipeline tests.
- Agent output validation tests.
- Prompt-injection and unsafe recommendation tests.

Frontend:

- TypeScript typecheck.
- No-dependency Node smoke tests for important routes, API client wiring, Settings privacy controls, and free-only data policy copy.

CI:

- GitHub Actions workflow for backend tests and frontend checks.
- Manual trigger only, so it does not automatically consume Actions minutes.

## Free-Only Rule

The CI workflow uses GitHub Actions, but it is manual-only by default. Use it only when your GitHub repository/account keeps Actions within free or included usage.

If GitHub Actions could bill you:

- Disable the workflow.
- Run the same commands locally.
- Do not add paid CI, paid security scanners, paid coverage tools, or paid dependency services.

## Local Commands

Backend:

```powershell
.venv\Scripts\python.exe -m pytest apps/api
```

Frontend:

```powershell
npm.cmd run typecheck:web
npm.cmd run test:web
```

## CI Checks

The workflow runs:

```text
python -m pip check
python -m pytest apps/api
npm run typecheck:web
npm run test:web
```

If your repo is public or your GitHub account has included Actions minutes you are comfortable using, you can later add a `pull_request` trigger. For now, CrocLens avoids automatic CI usage.

## Testing Concepts

Unit tests:

- Test one function or service in isolation.
- Example: portfolio calculations.

API tests:

- Test HTTP endpoints and response contracts.
- Example: `GET /api/v1/tax/insights`.

Agent output validation:

- Tests that assistant responses include confidence, limitations, sources, safety state, and do not make unsafe claims.

Smoke tests:

- Lightweight tests that prove critical files and wiring exist.
- Useful before heavier browser tests are introduced.

## Mini Assignment

Add one frontend smoke assertion that checks `/settings` includes export and delete controls.
