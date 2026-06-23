# Testing And CI

## Current Strategy

CrocLens now uses layered quality gates. The goal is to catch user-visible regressions while keeping tests deterministic and free-first.

Backend checks:

- API contract tests.
- Authentication and user isolation tests.
- Portfolio calculation tests.
- Database schema and Alembic migration discovery.
- Provider adapter tests with mocked clients.
- Stale cache and provider failure tests.
- Agent output validation tests.
- Prompt-injection and unsafe recommendation tests.

Frontend checks:

- TypeScript typecheck.
- Vitest behavior tests for auth, Croc Guide, and the BFF API client.
- Fast structural smoke tests for route and copy regressions.
- Next.js production build.
- Production dependency audit with `npm audit --omit=dev`.
- Playwright smoke test for the public landing page and signup path.

CI runs on:

- `pull_request`
- `push` to `main`
- `workflow_dispatch`

## Free-First Rule

The workflow uses GitHub Actions. Public repositories and many student/developer accounts have included minutes, but this is not guaranteed forever.

If GitHub Actions could bill you:

- Disable the workflow.
- Run the same commands locally.
- Do not add paid CI, paid security scanners, paid coverage tools, or paid dependency services.

## Local Commands

Backend:

```powershell
.venv\Scripts\python.exe -m pytest apps/api
.venv\Scripts\python.exe -m alembic -c apps/api/alembic.ini heads
```

Frontend:

```powershell
npm.cmd run typecheck:web
npm.cmd run test:unit --workspace @croclens/web
npm.cmd run test:web
npm.cmd run build:web
npm.cmd audit --omit=dev
```

Playwright smoke tests:

```powershell
npm.cmd run test:e2e --workspace @croclens/web
```

If Playwright browsers are missing locally:

```powershell
npx.cmd playwright install chromium
```

## CI Checks

The workflow runs:

```text
python -m pip check
python -m pytest apps/api
python -m alembic -c apps/api/alembic.ini heads
npm run typecheck:web
npm audit --omit=dev
npm run test:web
npm run build:web
npx playwright install --with-deps chromium
npm run test:e2e --workspace @croclens/web
```

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

Behavior tests:

- Render real React components and simulate user actions.
- Example: login validation, Croc Guide question submission, and API-client routing.

End-to-end tests:

- Run the app in a real browser and verify a user journey.
- Example: landing page to signup.

Accessibility checks:

- Future work should add axe-based assertions for major pages and dialogs.

## Mini Assignment

Add one Vitest test for a dashboard stale-data warning state.
