# CrocLens API Endpoints

## Current Status

The current MVP has FastAPI REST endpoints, local persisted authentication, a Next.js BFF proxy, and PostgreSQL-backed portfolio holdings/liabilities for authenticated users.

The backend lives in:

```text
apps/api
```

## API Style

CrocLens will start with REST APIs.

Why REST first:

- Easy to understand.
- Works well with Next.js.
- Pydantic makes request and response validation straightforward.
- Good fit for CRUD workflows and dashboard data.

GraphQL is not needed for the MVP.

## Implemented Phase 3 Endpoints

Phase 5 frontend integration currently uses:

- `GET /api/v1/portfolio/summary`
- `GET /api/v1/portfolio/records`
- `GET /api/v1/portfolio/holdings`
- `POST /api/v1/portfolio/holdings`
- `PUT /api/v1/portfolio/holdings/{holding_id}`
- `DELETE /api/v1/portfolio/holdings/{holding_id}`
- `GET /api/v1/portfolio/liabilities`
- `POST /api/v1/portfolio/liabilities`
- `PUT /api/v1/portfolio/liabilities/{liability_id}`
- `DELETE /api/v1/portfolio/liabilities/{liability_id}`
- `GET /api/v1/assets`
- `GET /api/v1/assets/detail-cards`
- `GET /api/v1/assets/{asset_id}/detail`
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `GET /api/v1/onboarding/options`
- `POST /api/v1/onboarding/profile`
- `GET /api/v1/action-plans`
- `POST /api/v1/action-plans/generate`
- `POST /api/v1/action-plans/items/{item_id}/complete`
- `POST /api/v1/action-plans/items/{item_id}/dismiss`
- `POST /api/v1/action-plans/items/{item_id}/reopen`
- `POST /api/v1/ai/assistant`
- `GET /api/v1/ai/agents`
- `GET /api/v1/data-providers/status`
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

Browser-facing frontend requests use a same-origin BFF proxy:

```text
/api/backend/api/v1/...
```

The BFF reads the HttpOnly `croclens_session` cookie and forwards it to FastAPI as a bearer token. The backend target can be overridden with:

```text
CROCLENS_API_URL
```

### Health

```http
GET /health
```

Purpose:

- Confirm the backend is running.

### Portfolio Summary

```http
GET /api/v1/portfolio/summary
```

Purpose:

- Return net worth, total assets, liabilities, allocation, and score summaries.
- Return PostgreSQL-backed user data when a valid session is present.
- Return sample data for unauthenticated demo access.

Phase 6 adds calculated fields:

- `total_assets`
- `total_liabilities`
- `net_worth`
- `allocation`
- `debt_impact`
- `scores`

Each score includes:

- `label`
- `value`
- `explanation`
- `formula`

### Portfolio Records

```http
GET /api/v1/portfolio/records
GET /api/v1/portfolio/holdings
POST /api/v1/portfolio/holdings
PUT /api/v1/portfolio/holdings/{holding_id}
DELETE /api/v1/portfolio/holdings/{holding_id}
GET /api/v1/portfolio/liabilities
POST /api/v1/portfolio/liabilities
PUT /api/v1/portfolio/liabilities/{liability_id}
DELETE /api/v1/portfolio/liabilities/{liability_id}
```

Purpose:

- Store and retrieve user-owned holdings and liabilities.
- Recalculate total assets, liabilities, allocation, debt impact, and cross-asset scores from persisted records.
- Return `401` when no valid session is provided.
- Return `404` when a user attempts to access another user's record.

Current scope:

- Manual entry first.
- The Portfolio page uses these endpoints for add, edit, delete, and post-mutation summary refreshes.
- No live brokerage connection.
- No direct trading instructions.
- Source metadata labels records as user-entered local development data.

### Assets

```http
GET /api/v1/assets
GET /api/v1/assets/{asset_id}
GET /api/v1/assets/detail-cards
GET /api/v1/assets/{asset_id}/detail
```

Purpose:

- Return asset lists, portfolio detail cards, and full beginner-friendly detail pages.

Phase 7 detail responses include:

- `what_this_is`
- `why_it_matters`
- `risk_explanation`
- `liquidity_explanation`
- `tax_complexity_explanation`
- `income_potential_explanation`
- `what_to_watch`
- `safe_next_steps`
- `confidence`
- `data_limitations`
- `source`
- `educational_disclaimer`

### Onboarding

```http
GET /api/v1/onboarding/options
POST /api/v1/onboarding/profile
```

Purpose:

- Collect beginner goals, risk comfort, time horizon, income range, retirement context, debt context, and manual assets.
- Return an educational risk profile that can personalize future dashboard, action plan, and AI assistant behavior.

The profile request includes:

- `investment_experience`
- `primary_goal`
- `risk_tolerance`
- `time_horizon`
- `income_range`
- `emergency_cash_months`
- `has_retirement_account`
- `employer_match`
- `retirement_contribution_percent`
- `has_mortgage`
- `has_student_loans`
- `has_credit_card_debt`
- `has_high_interest_debt`
- `manual_assets`

The profile response includes:

- `risk_profile`
- `risk_score`
- `summary`
- `personalization_notes`
- `recommended_first_steps`
- `confidence`
- `data_limitations`
- `source`
- `educational_disclaimer`

Current UX rule:

- `/signup` collects onboarding profile data during account creation.
- `/onboarding` redirects to `/signup` so onboarding is no longer a separate primary page.

### Auth

```http
POST /api/v1/auth/signup
POST /api/v1/auth/login
```

Purpose:

- Model account creation and login without adding a paid auth provider.
- Collect onboarding profile data during signup.
- Return a local development session token to the Next.js BFF.
- Store the browser session in an HttpOnly cookie from the frontend route handlers.
- Keep the raw session token out of browser JavaScript.

Signup request includes:

- `display_name`
- `email`
- `password`
- `onboarding_profile`

Important limitation:

- Local auth is for development. Production auth should use Cognito or another mature provider with verified email, password reset, JWT validation, session expiration, and abuse controls.

### Action Plans

```http
GET /api/v1/action-plans
POST /api/v1/action-plans/generate
```

Purpose:

- Return educational action plans and generate a mock plan from sample data.

### AI Assistant

```http
POST /api/v1/ai/assistant
GET /api/v1/ai/agents
```

Purpose:

- Accept a user question and return a safe structured assistant response.

Required request body:

```json
{
  "question": "How does today's market affect me?",
  "beginner_mode": true,
  "include_prompt_debug": false
}
```

Required safety fields in the response:

- `intent`
- `summary`
- `beginner_explanation`
- `suggested_next_steps`
- `confidence`
- `data_limitations`
- `sources`
- `safety`
- `agent_trace`
- `prompt_context`
- `safety_disclaimer`

`GET /api/v1/ai/agents` returns the Phase 10 agent registry, including implemented and stubbed agents.

Phase 9 intent examples:

- `portfolio`
- `debt`
- `retirement`
- `tax`
- `market`
- `risk`
- `education`
- `safety`

### Data Pipeline

```http
GET /api/v1/data-providers/status
GET /api/v1/data-pipeline/providers
POST /api/v1/data-pipeline/market-data/sample-ingest
GET /api/v1/data-pipeline/market-data/latest
GET /api/v1/market/snapshot
GET /api/v1/market/quotes/{symbol}
GET /api/v1/market/history/{symbol}?period=1M&interval=1d
GET /api/v1/portfolio/history
POST /api/v1/portfolio/refresh-prices
```

Purpose:

- Report normalized provider readiness for yfinance, CoinGecko, FRED public CSV, Treasury/Fiscal Data, and SEC EDGAR.
- List planned and implemented data providers.
- Run the deterministic sample market data ingestion pipeline.
- Return latest normalized sample market observations.

The provider status endpoint does not fetch live data by itself. It exposes configuration, capabilities, cache TTL, stale threshold, provider status, cache status, and data limitations.

Phase 21B adds live-capable provider adapters behind this registry. Phase 21C and 21D add persisted observations and market API endpoints that frontend surfaces can call without touching provider clients directly.

Phase 21D adds the first live-market API surface:

- `GET /api/v1/market/snapshot` returns the clearly labeled sample market snapshot used by the current dashboard.
- `GET /api/v1/market/quotes/{symbol}` retrieves a quote through the provider registry, persists it, and returns stale/unavailable metadata honestly.
- `GET /api/v1/market/history/{symbol}` supports `1M`, `3M`, `6M`, `YTD`, `1Y`, `5Y`, and `ALL` periods with `1d`, `1wk`, or `1mo` intervals.
- `POST /api/v1/portfolio/refresh-prices` refreshes authenticated public holdings and preserves manual/private values.
- `GET /api/v1/portfolio/history` returns stored net-worth snapshots only; it does not invent trend lines.

Every response includes provider/sample/stale/data-quality metadata and educational limitations.

Phase 22 frontend behavior:

- The dashboard market snapshot card calls `GET /api/v1/market/snapshot` and displays provider status, sample/stale labels, loading, and error states.
- The dashboard net-worth chart calls `GET /api/v1/portfolio/history` for signed-in users and shows an empty state when no stored snapshots exist.
- Demo visitors still see clearly labeled sample history, separate from persisted account data.
- Internal evaluation metrics live at `/internal/evaluation-metrics` and are not shown in beginner navigation.

The sample ingestion response includes:

- `pipeline_name`
- `dataset_id`
- `provider`
- `status`
- `extracted_count`
- `accepted_count`
- `rejected_count`
- `freshness_report`
- `quality_issues`
- `records`
- `confidence`
- `data_limitations`
- `sources`
- `educational_disclaimer`

Crypto market data is sample-only for now. CrocLens should not add paid or ambiguous freemium market data providers to the MVP.

### Market News Impact

```http
GET /api/v1/market-news/impact-summary
```

Purpose:

- Return sample news context.
- Map headlines to affected holdings.
- Explain why the news may matter in beginner-friendly language.
- Include confidence, limitations, source metadata, and educational disclaimer.

### Tax Insights

```http
GET /api/v1/tax/insights
POST /api/v1/tax/lots
PUT /api/v1/tax/lots/{lot_id}
DELETE /api/v1/tax/lots/{lot_id}
```

Purpose:

- Return sample tax lots for demo visitors or saved user tax lots for authenticated users.
- Let authenticated users create, update, and delete tax lots tied to their own holdings.
- Explain unrealized gains/losses and holding periods.
- Show educational tax-loss harvesting opportunities.
- Include wash-sale warning language and tax-advice limitations.
- Enforce ownership through the holding's portfolio owner.

### Retirement Plan

```http
GET /api/v1/retirement/plan
POST /api/v1/retirement/accounts
PUT /api/v1/retirement/accounts/{account_id}
DELETE /api/v1/retirement/accounts/{account_id}
```

Purpose:

- Return sample retirement accounts for demo visitors or saved retirement accounts for authenticated users.
- Let authenticated users create, update, and delete retirement accounts.
- Explain employer 401(k) match.
- Compare contribution scenarios.
- Include projection assumptions and limitations.

### Decision Journal

```http
GET /api/v1/journal/entries
POST /api/v1/journal/entries
PUT /api/v1/journal/entries/{entry_id}
DELETE /api/v1/journal/entries/{entry_id}
```

Purpose:

- Return sample decision journal entries for demo visitors or saved entries for authenticated users.
- Accept, update, and delete authenticated decision entries.
- Return rule-based process feedback.
- Track review status, actual outcome, and reflection fields for a learning loop.

### Watchlist

```http
GET /api/v1/watchlist
POST /api/v1/watchlist
PUT /api/v1/watchlist/{item_id}
DELETE /api/v1/watchlist/{item_id}
```

Purpose:

- Return sample watchlist intelligence for demo visitors or saved watchlist records for authenticated users.
- Accept, update, and delete authenticated watchlist items.
- Explain risk and opportunity notes without presenting the watchlist as a buy list.
- Prevent duplicate watchlist records per user and asset.

### Action Plans

```http
GET /api/v1/action-plans
POST /api/v1/action-plans/generate
POST /api/v1/action-plans/items/{item_id}/complete
POST /api/v1/action-plans/items/{item_id}/dismiss
POST /api/v1/action-plans/items/{item_id}/reopen
```

Purpose:

- Generate educational action plans from the authenticated user's saved portfolio, liabilities, and account context.
- Let users complete, dismiss, and reopen action items.
- Preserve safe wording, confidence, evidence, freshness, and limitations.
- Return sample action plans for demo visitors.

### Security And Privacy

```http
GET /api/v1/security/status
GET /api/v1/privacy/settings
PUT /api/v1/privacy/settings
GET /api/v1/privacy/export
DELETE /api/v1/privacy/data
```

Purpose:

- Show current MVP security controls.
- Persist privacy settings for authenticated users.
- Return user-specific export counts for authenticated users.
- Keep delete as a preview until production confirmation, audit logging, and background cleanup are added.
- Return sample privacy settings and export counts for demo visitors.

### Evaluation Metrics

```http
GET /api/v1/evaluation/metrics
```

Purpose:

- Return a local internal scorecard for product usefulness, AI safety, data quality, and reliability.
- Show metric targets, status, sample size, how each metric is measured, and limitations.
- Keep the MVP free-only by using deterministic sample metrics instead of paid analytics or monitoring tools.

Metric categories:

- `product`
- `ai_safety`
- `data_quality`
- `reliability`

## Planned Later Endpoints

### Liability Detail Pages

```http
GET /api/v1/liabilities
GET /api/v1/liabilities/{liability_id}
```

Purpose:

- Return debt and liability details.

## API Design Rules

Responses should:

- Use clear JSON shapes.
- Include source/freshness metadata when relevant.
- Avoid leaking stack traces.
- Use safe AI output contracts.

Requests should:

- Be validated by Pydantic.
- Reject invalid values with useful error messages.
- Avoid accepting unbounded text without limits.

Status codes:

- `200` for successful reads.
- `201` for created records.
- `400` for invalid user input.
- `404` for missing records.
- `422` for validation errors.
- `500` only for unexpected server failures.
