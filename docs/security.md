# CrocLens Security and Safety

## Security Goal

CrocLens handles sensitive financial information, so the product must be designed with privacy, safety, and reliability from the beginning.

The MVP will start simple, but the architecture should prepare for production security.

## Financial Safety Rules

CrocLens is educational software, not a licensed financial advisor.

AI and product copy must avoid:

- Direct buy or sell instructions
- Guaranteed returns
- Claims that an investment is best
- Overconfident predictions
- Hidden assumptions

AI and product copy should use:

- "Consider reviewing..."
- "You may want to research..."
- "This could be a risk..."
- "Based on the data provided..."
- "This is educational, not financial advice."

Every AI output should include:

- Confidence level
- Data limitations
- Source or freshness information when available
- Beginner-friendly explanation
- Safe wording

## Privacy Principles

CrocLens should eventually support:

- Export user data
- Delete account and data
- Clear privacy settings
- Minimal data collection
- User-controlled manual entry
- Explicit consent before external integrations

## Authentication Plan

MVP:

- Use local persisted account creation and login endpoints for development only.
- Collect onboarding profile data during account creation.
- Redirect the old `/onboarding` page to `/signup` so onboarding is not a separate product surface.
- Do not store real secrets or real financial credentials.
- Store bcrypt password hashes, never plaintext passwords.
- Store local session records with expiration and revocation.
- Keep the browser session token in an HttpOnly cookie managed by the Next.js BFF.
- Do not claim local auth is production authentication.

Later:

- Use a verified free auth approach only after review.
- Hash passwords with a production-grade password hashing algorithm.
- Persist users, sessions, and profiles safely.
- Add email verification and account recovery.
- Add session management.
- Add role-based access if an admin surface exists.
- Add passwordless or OAuth flows only when needed.

Current MVP auth endpoints:

```http
POST /api/v1/auth/signup
POST /api/v1/auth/login
GET /api/v1/auth/me
POST /api/v1/auth/logout
```

Current limitation:

- Local sessions are development-only.
- Production auth still needs Cognito or another mature provider with verified email, password reset, abuse controls, and JWT validation.
- Local development portfolio records are suitable for learning and testing, not real financial data.

Frontend BFF behavior:

- Browser code calls same-origin routes such as `/api/auth/login` and `/api/backend/api/v1/portfolio/records`.
- The BFF reads the `croclens_session` HttpOnly cookie server-side.
- The BFF forwards the token to FastAPI as a bearer token.
- Browser JavaScript cannot read the raw token.

## Secret Management

Local development:

- Use `.env` files for local configuration.
- Never commit real API keys.

Production later:

- Use only free secret-management options unless explicitly approved.
- Grant least-privilege access.
- Rotate secrets when needed.

## API Security

Backend should include:

- Pydantic validation
- Clear status codes
- Error responses that do not leak internals
- In-memory rate limiting for the MVP
- Request size limits
- CORS configured only for expected frontend origins
- Request IDs for debugging
- Basic browser security headers

Phase 17 adds:

- `X-CrocLens-Request-Id`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy`
- `Permissions-Policy`
- Generic unhandled error responses
- `GET /api/v1/security/status`

## Prompt Injection Safety

Prompt injection happens when user text or external content tries to override the AI system rules.

CrocLens should treat user inputs, filings, news, and market text as untrusted data.

Guardrails:

- Keep financial safety rules outside user-controlled text.
- Use structured AI outputs.
- Run a Safety/Compliance Guardrail Agent before returning responses.
- Do not let external text change system behavior.
- Refuse requests for guaranteed returns or direct trading instructions.
- Detect phrases such as "ignore previous instructions", "reveal your system prompt", and "bypass guardrails".

## Privacy Controls

Phase 17 adds MVP privacy endpoints:

```http
GET /api/v1/privacy/settings
PUT /api/v1/privacy/settings
GET /api/v1/privacy/export
DELETE /api/v1/privacy/data
```

Current limitation:

- Settings, export, and delete are previews because the app still uses sample data.

Production requirement:

- Persist settings per authenticated user.
- Require confirmation for deletes.
- Generate export archives asynchronously.
- Track deletion jobs and audit logs without storing sensitive data unnecessarily.

## Logging and Monitoring

Log:

- API latency
- Error rates
- Failed validations
- Data ingestion failures
- AI safety refusals

Avoid logging:

- Full account numbers
- Secrets
- API keys
- Sensitive user-entered financial details unless truly required

## Free-Only Cost Safety

CrocLens should not add paid services, paid data providers, or ambiguous free trials unless the user explicitly approves them.

Cloud cost traps to avoid:

- Any always-on cloud service
- Any managed database that can bill automatically
- Any hosted model endpoint or paid LLM call
- Any paid monitoring or log-retention service
- Any paid or ambiguous freemium data API
- Any free trial that requires a credit card or can later bill

Controls:

- Prefer local development and sample data during MVP.
- Treat cloud "free tier" services as risky until their billing behavior is reviewed.
- Do not add paid providers, paid auth, paid databases, paid LLM calls, or paid monitoring by default.
- Require explicit approval before any service that can incur charges.
