# CrocLens AWS Deployment Plan

## Current Status

Phase 0 defines the deployment direction. Deployment work will happen in Phase 20.

## MVP Deployment Principles

- Keep costs low.
- Avoid always-on services unless needed.
- Prefer managed services with clear free-tier behavior.
- Add budget alerts before deploying paid infrastructure.
- Start with simple deployment before production complexity.

## Candidate AWS Architecture

```text
User
  |
  v
CloudFront
  |
  v
S3 static frontend or Amplify

API Gateway
  |
  v
Lambda running FastAPI through Mangum
  |
  v
PostgreSQL

Supporting services:
  SSM Parameter Store
  CloudWatch
  AWS Budgets
```

## Frontend Options

### S3 + CloudFront

Pros:

- Low cost.
- Production-grade static hosting.
- Good caching.

Cons:

- More setup than Amplify.
- Best for static export or separated frontend deployments.

### Amplify

Pros:

- Easier setup for Next.js.
- Git-based deployment flow.

Cons:

- Costs and behavior need careful review as the app grows.

## Backend Options

### Lambda + API Gateway + Mangum

Pros:

- Scales to zero.
- Good for low-traffic MVP.
- Avoids always-on compute.

Cons:

- Cold starts.
- Some FastAPI patterns need serverless awareness.
- Long-running jobs should not live in request handlers.

### Small Container or EC2 Service

Pros:

- More familiar server model.
- Easier for long-running processes.

Cons:

- Can cost money while idle.
- Requires more operations work.

## Database Options

### RDS PostgreSQL

Pros:

- Managed relational database.
- Production-friendly.

Cons:

- Can become a cost trap if left running outside free-tier or credits.

### Free External Postgres

Pros:

- Good for MVP learning.
- Often cheaper to start.

Cons:

- Provider limits.
- Network and security configuration still matter.

## Cost Traps

Avoid or review carefully:

- NAT Gateway
- Always-on EC2
- RDS left running
- OpenSearch
- SageMaker endpoints
- Heavy Bedrock usage
- Large CloudWatch logs
- Load Balancers
- Paid data APIs

## Cost Controls

Before deploying:

- Create AWS Budget alerts.
- Set CloudWatch log retention.
- Use smallest possible database tier.
- Avoid NAT Gateway unless truly needed.
- Avoid paid data providers in MVP.
- Review monthly cost estimate.

