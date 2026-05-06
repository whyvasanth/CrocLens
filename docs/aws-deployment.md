# CrocLens Free-Only Deployment Policy

## Current Status

Deployment work is planned for Phase 20, but CrocLens is currently a free-only learning project.

Do not deploy to AWS or any paid cloud service unless the user explicitly approves it later.

## Free-Only Rule

CrocLens should use:

- Local development.
- GitHub for source control.
- Free/open-source libraries.
- Sample data.
- Verified no-cost public data sources.

CrocLens should not use by default:

- Paid cloud hosting.
- Paid databases.
- Paid auth providers.
- Paid data APIs.
- Paid LLM calls.
- Paid monitoring.
- Free trials that require a credit card or can later bill.

## Phase 20 Direction

When deployment becomes necessary, evaluate only options that are verifiably free at the time of implementation.

Before choosing any service, document:

- Whether a credit card is required.
- Whether the service can bill automatically.
- Usage limits.
- Sleep/idle behavior.
- Data retention limits.
- What happens when limits are exceeded.

## Cost Traps To Avoid

Avoid services that can create charges without careful review:

- NAT Gateway.
- Always-on virtual machines.
- Managed relational databases.
- Search clusters.
- Hosted model endpoints.
- Heavy logs.
- Load balancers.
- Paid data APIs.

## MVP Deployment Preference

Until Phase 20, run CrocLens locally:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --app-dir apps/api --host 127.0.0.1 --port 8000
npm.cmd run dev:web
```

The project should remain useful without paid infrastructure.
