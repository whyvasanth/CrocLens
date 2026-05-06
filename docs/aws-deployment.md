# CrocLens Free-Only Deployment Plan

## Current Status

Phase 20 adds a local Docker deployment plan.

Do not deploy to AWS or any paid cloud service by default.

CrocLens remains a free-only learning project until the user explicitly approves a paid or potentially billable service.

## What Phase 20 Adds

Files:

- `.dockerignore`
- `.env.example`
- `apps/api/Dockerfile`
- `apps/web/Dockerfile`
- `docker-compose.yml`

Commands:

- `npm.cmd run docker:up`
- `npm.cmd run docker:down`

The containers run:

- FastAPI backend on `http://127.0.0.1:8000`
- Next.js frontend on `http://localhost:3000`

No paid APIs, cloud services, hosted databases, hosted auth, paid LLM calls, or paid monitoring tools are required.

## Local Deployment Architecture

```text
Browser
  |
  | http://localhost:3000
  v
Next.js web container
  |
  | fetch http://localhost:8000/api/v1/...
  v
FastAPI api container
  |
  | local sample data only
  v
No paid external service
```

## Why Docker

Docker gives the project a repeatable runtime.

Without Docker:

- You install Node, Python, dependencies, and environment variables directly on your machine.
- Another developer may have a different Python or Node version.

With Docker:

- The backend image defines its Python runtime.
- The frontend image defines its Node runtime.
- `docker-compose.yml` describes how the services run together.
- The app can be started with one command.

## Docker Concepts

Image:

- A packaged app runtime.
- Example: the CrocLens API image contains Python, FastAPI dependencies, and API code.

Container:

- A running instance of an image.
- Example: the API container listens on port `8000`.

Dockerfile:

- Instructions for building one image.
- CrocLens has one Dockerfile for the API and one for the web app.

Compose:

- A YAML file that runs multiple containers together.
- CrocLens uses `docker-compose.yml` to run `api` and `web`.

Health check:

- A small command that tells Docker whether a service is ready.
- The web container waits for the API health check before starting.

Build argument:

- A value passed during image build.
- CrocLens passes `NEXT_PUBLIC_CROCLENS_API_URL=http://localhost:8000` so the browser can call the local API.

## How To Run With Docker

Prerequisite:

- Docker Engine, Docker Desktop for personal use, or another Docker-compatible local runtime.

Start both services:

```powershell
npm.cmd run docker:up
```

Open:

```text
http://localhost:3000/dashboard
http://127.0.0.1:8000/docs
```

Stop services:

```powershell
npm.cmd run docker:down
```

Equivalent raw Docker command:

```powershell
docker compose up --build
docker compose down
```

## How To Run Without Docker

Backend:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --app-dir apps/api --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
npm.cmd run dev:web
```

Open:

```text
http://localhost:3000/dashboard
```

## How To Validate

Backend tests:

```powershell
.venv\Scripts\python.exe -m pytest apps/api
```

Frontend checks:

```powershell
npm.cmd run typecheck:web
npm.cmd run test:web
```

Docker Compose syntax:

```powershell
docker compose config
```

If Docker is installed but the engine is stopped, you may see an error like:

```text
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

Fix:

- Start Docker Desktop or your local Docker engine.
- Wait until Docker says it is running.
- Re-run `docker compose build` or `npm.cmd run docker:up`.

Optional production web build:

```powershell
npm.cmd run build:web
```

## Environment Variables

Local example:

```text
NEXT_PUBLIC_CROCLENS_API_URL=http://127.0.0.1:8000
RATE_LIMIT_PER_MINUTE=300
```

Rules:

- Do not commit real secrets.
- Do not add paid API keys for the MVP.
- Do not add cloud credentials to `.env`.
- Keep `.env.example` safe and non-sensitive.

## Free-Only Deployment Rule

CrocLens should use:

- Local development.
- Local Docker.
- GitHub source control.
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

## AWS Position

AWS is not part of the active MVP deployment.

Do not deploy to AWS until all of these are true:

- The user explicitly approves AWS.
- Current pricing is verified on official AWS pages.
- A billing alert is configured before creating resources.
- A written shutdown checklist exists.
- The deployment can be deleted cleanly.
- The user understands which services can bill.

This document intentionally does not promise that any AWS architecture is free. Cloud pricing changes, free-tier rules change, and mistakes can create charges.

## Future AWS Shape, Only If Explicitly Approved

If AWS is approved later, the lowest-complexity educational architecture to evaluate would be:

```text
S3 or Amplify static frontend
        |
        v
API Gateway
        |
        v
Lambda running FastAPI through Mangum
        |
        v
External free Postgres or carefully reviewed database option
```

But for the current MVP:

- No AWS account is required.
- No AWS service is created.
- No managed database is created.
- No cloud auth provider is created.
- No paid model endpoint is created.

## Cost Traps To Avoid

Avoid services that can create charges without careful review:

- NAT Gateway.
- Always-on EC2.
- RDS left running.
- OpenSearch.
- SageMaker endpoints.
- Bedrock heavy usage.
- Large CloudWatch logs.
- Load balancers.
- Paid data APIs.
- Managed streaming services.
- Accidentally public storage with large egress.

## Production Upgrade Path

When CrocLens is ready for production, the deployment work should be split into smaller phases:

1. Add real authentication.
2. Add persistent database storage.
3. Add secrets management.
4. Add migration automation.
5. Add structured logs and privacy-safe metrics.
6. Add backup and restore plan.
7. Add deployment rollback plan.
8. Add cost monitoring before cloud resources.

For now, Docker gives CrocLens a repeatable local deployment without paid infrastructure.
