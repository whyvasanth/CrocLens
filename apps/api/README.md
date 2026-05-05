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

