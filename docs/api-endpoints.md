# CrocLens API Endpoints

## Current Status

Phase 0 defines the planned API surface. The FastAPI backend will be implemented in Phase 3.

## API Style

CrocLens will start with REST APIs.

Why REST first:

- Easy to understand.
- Works well with Next.js.
- Pydantic makes request and response validation straightforward.
- Good fit for CRUD workflows and dashboard data.

GraphQL is not needed for the MVP.

## Planned MVP Endpoints

### Health

```http
GET /health
```

Purpose:

- Confirm the backend is running.

### Portfolio Summary

```http
GET /portfolio/summary
```

Purpose:

- Return net worth, total assets, liabilities, allocation, and score summaries.

### Assets

```http
GET /assets
GET /assets/{asset_id}
```

Purpose:

- Return asset lists and asset detail data.

### Liabilities

```http
GET /liabilities
GET /liabilities/{liability_id}
```

Purpose:

- Return debt and liability details.

### Action Plans

```http
GET /action-plans
POST /action-plans/generate
```

Purpose:

- Return educational action plans and generate new plans from user data.

### AI Assistant

```http
POST /ai/assistant
```

Purpose:

- Accept a user question and return a safe structured assistant response.

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

