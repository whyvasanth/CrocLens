# CrocLens

See your money clearly.

CrocLens is a small beginner-friendly investment dashboard. It lets a user search for a stock or ETF ticker, fetches latest available market data from `yfinance`, shows a simple price chart, displays a small demo ETF portfolio, and explains the numbers in plain language with Croc Guide.

CrocLens is educational software, not financial advice. It does not tell users to buy or sell investments and does not promise returns.

## MVP Features

- Landing page with ticker search.
- Dashboard page with a clearly labeled demo portfolio.
- Asset detail page for stock/ETF quote data.
- Latest available price, recent change, volume, range, and market cap when available.
- Six-month historical price chart.
- Rule-based Croc Guide explanation.
- Loading, empty, and error states.

## Tech Stack

Frontend:

- Next.js
- TypeScript
- Tailwind CSS
- Recharts
- Lucide icons

Backend:

- FastAPI
- Pydantic
- yfinance
- pytest

## Repository Structure

```text
CrocLens/
  apps/
    api/
      app/
        main.py          # FastAPI app and routes
        config.py        # Small environment config
        schemas.py       # API response models
        market_data.py   # yfinance access
        portfolio.py     # demo portfolio
        guide.py         # rule-based explanation
      tests/
        test_api.py
      requirements.txt
    web/
      app/
        page.tsx
        dashboard/page.tsx
        assets/[symbol]/page.tsx
        layout.tsx
        globals.css
      components/
      lib/
      scripts/smoke-test.mjs
```

## Environment Variables

Create `.env` only if you need to override defaults.

```text
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
YFINANCE_TIMEOUT_SECONDS=12
```

## Setup

Install frontend dependencies:

```powershell
npm install
```

Install backend dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r apps/api/requirements.txt
```

## Run Locally

Start the API:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir apps/api --host 127.0.0.1 --port 8000
```

Start the web app in another terminal:

```powershell
npm run dev:web
```

Open:

```text
http://127.0.0.1:3000
```

## Tests

Backend:

```powershell
.venv\Scripts\python.exe -m pytest apps/api
```

Frontend:

```powershell
npm run typecheck:web
npm run test:web
npm run build:web
```

Manual API checks:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/quote/VTI
Invoke-RestMethod http://127.0.0.1:8000/api/history/VTI
Invoke-RestMethod http://127.0.0.1:8000/api/demo-portfolio
```

## Known Limitations

- `yfinance` is unofficial and may be delayed, incomplete, rate-limited, or temporarily unavailable.
- The demo portfolio is sample data only.
- Croc Guide is deterministic and educational; it is not an LLM and not a financial advisor.
- The app intentionally stays small: no accounts, persistence, advanced planning, news analysis, or trading features.
