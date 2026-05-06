# CrocLens Evaluation Metrics

## Current Status

Phase 19 adds a local evaluation metrics slice:

- Backend endpoint: `GET /api/v1/evaluation/metrics`
- Frontend page: `/evaluation-metrics`
- Backend tests for metric coverage, targets, limitations, and AI safety metrics
- No paid analytics, monitoring, experimentation, or tracking tool

The metrics are deterministic sample metrics. They teach the structure before CrocLens collects real privacy-aware product events.

## Why Metrics Matter

CrocLens is an AI fintech education product. It needs to be:

- Useful: beginners can complete key workflows.
- Clear: Croc Guide explanations are understandable.
- Safe: AI outputs avoid direct trading instructions and guaranteed-return claims.
- Fresh: data surfaces show source and as-of context.
- Reliable: API calls stay fast and errors are visible.

For an AI product, a fluent answer is not enough. The answer must be grounded, safe, limited, and understandable.

## Metrics Architecture

```text
Frontend events later
        |
        v
Privacy-aware event log later
        |
        v
Metric calculation job later
        |
        v
GET /api/v1/evaluation/metrics
        |
        v
/evaluation-metrics internal dashboard
```

Phase 19 starts at the API contract and UI level using sample metrics. Later phases can replace the sample service with real calculations from logs, tests, and observability data.

## Metric Categories

### Product Metrics

Product metrics answer whether CrocLens is useful.

Current sample metrics:

- Onboarding completion rate
- Portfolio creation rate
- Action plan usage rate

Why they matter:

- If users cannot finish onboarding, the product is too confusing.
- If users cannot create a basic portfolio, the dashboard has no value.
- If users ignore action plans, the guidance may not be clear or useful.

### AI Safety Metrics

AI safety metrics answer whether Croc Guide is helpful without becoming unsafe.

Current sample metrics:

- AI clarity score
- Hallucination check pass rate
- Unsafe recommendation rate

Why they matter:

- Beginner users may overtrust confident AI language.
- Every AI output needs confidence, data limitations, sources, and safe wording.
- A response that says "buy this" or promises returns should fail evaluation.

### Data Quality Metrics

Data quality metrics answer whether users can trust the context shown in the app.

Current sample metric:

- Data freshness coverage

Why it matters:

- Finance data changes quickly.
- Even sample data should be clearly labeled.
- Production data should show source, as-of time, and limitations.

### Reliability Metrics

Reliability metrics answer whether the app works consistently.

Current sample metrics:

- Median API latency
- API error rate

Why they matter:

- Slow or failing APIs break user trust.
- Reliability issues should be visible before users report them.

## Current API Shape

```http
GET /api/v1/evaluation/metrics
```

Each metric includes:

- `id`
- `label`
- `category`
- `value`
- `unit`
- `target`
- `direction`
- `status`
- `sample_size`
- `beginner_explanation`
- `how_measured`
- `limitations`

The response also includes:

- `headline`
- `beginner_summary`
- `quality_checks`
- `recommended_reviews`
- `confidence`
- `data_limitations`
- `sources`
- `educational_disclaimer`

## Free-Only Rule

CrocLens should not add paid analytics or monitoring tools for the MVP.

Allowed for now:

- Local sample metrics
- Backend tests
- Frontend smoke tests
- Manual review rubrics
- Local logs
- Free included GitHub Actions usage only when intentionally run

Avoid for MVP:

- Paid analytics tools
- Paid session replay
- Paid APM tools
- Paid experimentation platforms
- External trackers that collect sensitive financial behavior

## Privacy Rule

Future product analytics should be opt-in, privacy-aware, and minimal.

Do collect later:

- Feature usage counts
- Completion events
- Error categories
- Latency aggregates
- AI output validation results

Do not collect:

- Full account numbers
- Exact sensitive financial history unless required by a user action
- Raw assistant conversations without explicit consent
- Secrets, tokens, or credentials
- External tracking identifiers for the MVP

## How To Run

Start the API:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --app-dir apps/api --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/api/v1/evaluation/metrics
```

Start the frontend:

```powershell
npm.cmd run dev:web
```

Open:

```text
http://localhost:3000/evaluation-metrics
```

## How To Test

Backend:

```powershell
.venv\Scripts\python.exe -m pytest apps/api
```

Frontend:

```powershell
npm.cmd run typecheck:web
npm.cmd run test:web
```

## Production Upgrade Path

Later, this can evolve into:

- Event table for privacy-safe product events
- Daily batch metric calculations
- AI response evaluation dataset
- Human review queue for high-risk AI outputs
- Data freshness checks per provider
- Latency and error aggregation from server logs

The MVP stays simple so the metric definitions are understandable before production data collection begins.
