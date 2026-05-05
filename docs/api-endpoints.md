# CrocLens API Endpoints

## Current Status

Phase 3 implements the first FastAPI backend skeleton with mock data only.

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
- `GET /api/v1/action-plans`

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

### Assets

```http
GET /api/v1/assets
GET /api/v1/assets/{asset_id}
```

Purpose:

- Return asset lists and asset detail data.

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
```

Purpose:

- Accept a user question and return a safe structured assistant response.

Required request body:

```json
{
  "question": "How does today's market affect me?",
  "beginner_mode": true
}
```

Required safety fields in the response:

- `confidence`
- `data_limitations`
- `sources`
- `safety_disclaimer`

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
