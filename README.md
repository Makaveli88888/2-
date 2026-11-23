# JOKER OS

**Repo:** [Makaveli88888/2-](https://github.com/Makaveli88888/2-)  
**Wersja:** 1.0.0 foundation — hybrid AI + PostgreSQL + JWT

JOKER OS is a Polish-speaking assistant foundation with an allow-listed tool layer and a path toward a multi-agent architecture. Orchestrator, Trickster, Sceptyk and Executor are currently workflow roles in one agent loop, not independent autonomous agents.

## Implemented in feature/joker-os-v1

- FastAPI API for chat, health, tools and conversation history.
- Hybrid model routing: OpenAI primary, xAI/Grok fallback (configurable).
- PostgreSQL persistence through SQLAlchemy.
- Signed HS256 JWT authentication on every API route except `/health`.
- Conversation ownership enforced by the authenticated JWT subject.
- Redis 7 provisioned in Docker Compose for the next cache/queue integration; it is not yet used by the request path.
- Existing allow-listed tools: AST calculator and UTC clock.
- Docker Compose health checks for PostgreSQL and Redis.

## Local setup

```bash
python -m venv .venv
# activate the virtual environment
pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY`, `XAI_API_KEY`, `JWT_SECRET` (at least 32 random characters), and `POSTGRES_PASSWORD`. For local PostgreSQL, set `DATABASE_URL` to your local server address. Then run:

```bash
uvicorn app.main:app --reload
```

## Docker setup

```bash
cp .env.example .env
# Set JWT_SECRET, POSTGRES_PASSWORD, and at least one model API key.
docker compose up --build
```

The API binds to `127.0.0.1:8000`; PostgreSQL and Redis are not published to the host. Put a TLS reverse proxy in front before remote/public use.

## Provision a user token

There is intentionally no public token-issuance endpoint. A trusted operator can mint a short-lived token:

```bash
python -m scripts.create_token makaveli
```

The resulting token is passed by the client as `Authorization: Bearer <token>`. Do not put JWT secrets or provider API keys in frontend code.

## Tests

```bash
python -m unittest discover -s tests -v
```

The conversation-store tests use SQLite in-memory/temp files for fast isolation checks; production defaults to PostgreSQL.

## Security notes / remaining work

See [docs/SECURITY_V1.md](docs/SECURITY_V1.md). This foundation does not yet include rate limiting, refresh-token lifecycle, schema migrations, Redis runtime integration, a full audit-event pipeline, or Telegram Mini App `initData` verification and real Stars payment callbacks. The standalone Telegram adapter has not yet been migrated to the hybrid provider and JWT model.
