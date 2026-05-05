# CrocLens API

Phase 3 adds the first FastAPI backend skeleton for CrocLens.

The API uses mock data only. There is no database yet, no authentication, and no real market data integration.

## Local Setup

From the repo root:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r apps/api/requirements.txt
```

Run the API:

```bash
python -m uvicorn app.main:app --reload --app-dir apps/api --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Test

```bash
python -m pytest apps/api
```

## Current Endpoints

- `GET /health`
- `GET /api/v1/portfolio/summary`
- `GET /api/v1/assets`
- `GET /api/v1/assets/{asset_id}`
- `GET /api/v1/action-plans`
- `POST /api/v1/action-plans/generate`
- `POST /api/v1/ai/assistant`

## Database Schema

Phase 4 adds SQLAlchemy models and an Alembic initial migration.

The schema is defined in:

```text
apps/api/app/models/entities.py
```

The initial migration is:

```text
apps/api/alembic/versions/20260505_0001_initial_schema.py
```

Set a PostgreSQL connection string when you are ready to run migrations:

```bash
set DATABASE_URL=postgresql+psycopg://croclens:croclens@localhost:5432/croclens
```

Then run from the repo root:

```bash
alembic -c apps/api/alembic.ini upgrade head
```

No live database is required for Phase 4 tests.

