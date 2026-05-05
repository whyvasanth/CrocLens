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

- Start with no real user auth or simple local demo auth if needed.
- Do not store real secrets or real financial credentials.

Later:

- Use AWS Cognito or a managed auth provider.
- Add session management.
- Add role-based access if an admin surface exists.
- Add passwordless or OAuth flows only when needed.

## Secret Management

Local development:

- Use `.env` files for local configuration.
- Never commit real API keys.

AWS later:

- Use SSM Parameter Store or Secrets Manager.
- Grant least-privilege IAM access.
- Rotate secrets when needed.

## API Security

Backend should include:

- Pydantic validation
- Clear status codes
- Error responses that do not leak internals
- Rate limiting in a later phase
- Request size limits
- CORS configured only for expected frontend origins

## Prompt Injection Safety

Prompt injection happens when user text or external content tries to override the AI system rules.

CrocLens should treat user inputs, filings, news, and market text as untrusted data.

Guardrails:

- Keep financial safety rules outside user-controlled text.
- Use structured AI outputs.
- Run a Safety/Compliance Guardrail Agent before returning responses.
- Do not let external text change system behavior.
- Refuse requests for guaranteed returns or direct trading instructions.

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

## AWS Cost Safety

Cost traps to avoid:

- NAT Gateway
- Always-on EC2
- RDS left running
- OpenSearch
- SageMaker endpoints
- Heavy Bedrock usage
- Large CloudWatch logs
- Load Balancers
- Paid data APIs

Controls:

- AWS Budget alerts
- CloudWatch log retention
- Small free-tier compatible services
- Manual review before adding paid providers

