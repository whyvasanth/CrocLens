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
- `POST /api/v1/ai/assistant`
- `GET /api/v1/ai/agents`
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
GET /api/v1/data-pipeline/providers
POST /api/v1/data-pipeline/market-data/sample-ingest
GET /api/v1/data-pipeline/market-data/latest
```

Purpose:

- List planned and implemented data providers.
- Run the deterministic sample market data ingestion pipeline.
- Return latest normalized sample market observations.

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
```

Purpose:

- Return sample tax lots.
- Explain unrealized gains/losses and holding periods.
- Show educational tax-loss harvesting opportunities.
- Include wash-sale warning language and tax-advice limitations.

### Retirement Plan

```http
GET /api/v1/retirement/plan
```

Purpose:

- Return sample retirement accounts.
- Explain employer 401(k) match.
- Compare contribution scenarios.
- Include projection assumptions and limitations.

### Decision Journal

```http
GET /api/v1/journal/entries
POST /api/v1/journal/entries
```

Purpose:

- Return sample decision journal entries.
- Accept a new decision entry preview.
- Return rule-based process feedback.

### Watchlist

```http
GET /api/v1/watchlist
POST /api/v1/watchlist
```

Purpose:

- Return sample watchlist intelligence.
- Accept a new watchlist item preview.
- Explain risk and opportunity notes without presenting the watchlist as a buy list.

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
- Preview user privacy preferences.
- Preview data export and delete workflows.
- Support Settings page controls before persistent auth and storage are added.

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

### Watchlist

```http
GET /watchlist
POST /watchlist
```

Purpose:

- Track assets or markets the user wants to monitor.

### Decision Journal

```http
GET /journal
POST /journal
```

Purpose:

- Store user decisions and review notes.

### Liabilities

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
