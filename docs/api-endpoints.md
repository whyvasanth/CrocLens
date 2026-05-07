# CrocLens API Endpoints

## Current Status

Phase 19 extends the FastAPI backend with an evaluation metrics endpoint for product quality, AI safety, data freshness, and reliability.

Latest product refinement adds mock account endpoints so signup can collect onboarding profile data during account creation.
Phase 21 adds data provider endpoints and LLM-ready AI orchestration endpoints while keeping existing mock flows compatible.

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
- `POST /api/v1/ai/chat`
- `POST /api/v1/ai/action-plan`
- `POST /api/v1/ai/explain-asset`
- `POST /api/v1/ai/portfolio-review`
- `GET /api/v1/data/providers`
- `GET /api/v1/data/freshness`
- `GET /api/v1/market/price/{symbol}`
- `GET /api/v1/market/history/{symbol}`
- `GET /api/v1/market/indicators/{symbol}`
- `GET /api/v1/crypto/price/{coin_id}`
- `GET /api/v1/macro/series/{series_id}`
- `GET /api/v1/rates/treasury`
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

The frontend API base URL defaults to:

```text
http://127.0.0.1:8000
```

It can be overridden with:

```text
NEXT_PUBLIC_CROCLENS_API_URL
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
- Return a mock session token and security limitations.

Signup request includes:

- `display_name`
- `email`
- `password`
- `onboarding_profile`

Important limitation:

- These are MVP mock endpoints. Production auth must hash passwords, persist users, verify email, protect sessions, add recovery flows, and apply rate limits.

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
POST /api/v1/ai/chat
POST /api/v1/ai/action-plan
POST /api/v1/ai/explain-asset
POST /api/v1/ai/portfolio-review
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

`GET /api/v1/ai/agents` returns the Phase 21 consolidated 8-agent registry.

The new Phase 21 AI endpoints return:

- `summary`
- `reasoning_summary`
- `action_items`
- `risks`
- `confidence`
- `data_sources`
- `data_freshness`
- `limitations`
- `safety_flags`
- `agent_trace`
- `safety_disclaimer`

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
GET /api/v1/data/providers
GET /api/v1/data/freshness
GET /api/v1/market/price/{symbol}
GET /api/v1/market/history/{symbol}
GET /api/v1/market/indicators/{symbol}
GET /api/v1/crypto/price/{coin_id}
GET /api/v1/macro/series/{series_id}
GET /api/v1/rates/treasury
```

Purpose:

- List planned and implemented data providers.
- Run the deterministic sample market data ingestion pipeline.
- Return latest normalized sample market observations.
- Route optional live provider requests through Phase 21 free/free-tier providers.
- Fall back to deterministic sample data when providers are missing, unconfigured, rate-limited, or unavailable.

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
