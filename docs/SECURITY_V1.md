# JOKER OS v1 — security baseline

## Authentication and identity
- Every API route except `/health` requires a signed HS256 JWT in the Authorization Bearer header.
- Tokens are provisioned by a trusted operator using `app.security.create_access_token`; there is intentionally no public token-issuance endpoint.
- The JWT subject (`sub`) is the user identity. The API never accepts an owner/user ID from request JSON.
- Set a high-entropy `JWT_SECRET` (at least 32 random bytes). Rotating it invalidates existing tokens.

## Data isolation
- Every conversation has one immutable owner ID.
- Reads, writes and deletes verify the authenticated subject against the stored owner.
- A mismatched or unknown conversation is returned as not found to avoid leaking its existence.

## AI providers
- Hybrid mode tries OpenAI first and xAI second. Provider errors are reduced to provider names and exception classes; secrets and raw upstream messages are not returned to clients.
- API keys are environment variables only. Never commit real keys or place them in frontend code.

## Deployment
- PostgreSQL is the default database. Redis is provisioned in Compose for the next queue/cache integration; this release does not yet depend on Redis at runtime.
- Terminate TLS at a trusted reverse proxy. Do not expose the API directly to the public internet without TLS and rate limiting.
- Keep `.env` out of version control. Use managed secrets in production.

## Remaining hardening
Rate limiting, refresh-token lifecycle, key rotation without global logout, database migration tooling, structured audit events, and Telegram Mini App `initData` validation remain follow-up work. The current release does not claim those controls are implemented.
