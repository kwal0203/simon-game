# Simon Game

A production-style Simon game with a React frontend, FastAPI backend, PostgreSQL, Redis cache, and internet deployment on AWS.

## Features

- Browser-playable Simon game UI
- Score submission and top-100 leaderboard API
- Read/write DB split support:
  - writes to primary database
  - reads from replica database
- Redis cache-aside leaderboard caching
- App-side rate limiting on score submissions
- Nginx reverse proxy with HTTPS in deployment
- Cloudflare CDN/proxy in front of origin

## Architecture

- **Frontend**: React + Vite (`apps/web`)
- **API**: FastAPI (`apps/api`)
- **Database**: PostgreSQL + Alembic migrations (`database/migrations`)
- **Cache**: Redis
- **Reverse proxy**: Nginx (`ops/nginx`)
- **Infra/ops docs**: `docs/`

## Repository Layout

- `apps/web` - frontend app and web tests
- `apps/api` - FastAPI app, DB access, API tests
- `database/migrations` - Alembic migration config and revisions
- `ops/nginx` - Nginx Docker image and runtime config
- `docs` - design, runbook, and deployment checklists

## Quick Start (Local Docker)

1. Set local environment variables in a root `.env` file:

```dotenv
DATABASE_WRITE_URL=postgresql+psycopg://postgres:localdev@db:5432/simon
DATABASE_READ_URL=postgresql+psycopg://postgres:localdev@db:5432/simon
REDIS_URL=redis://redis:6379/0
```

2. Start services:

```bash
docker compose up --build -d
```

3. Run migrations:

```bash
docker compose run --rm migrate
```

4. Open the app:

- `http://localhost`

## API Endpoints

- `GET /v1/leaderboard`
- `POST /v1/scores`
- `GET /health/db` (read path)
- `GET /health/db/write` (write path)

## Local Development (without Docker for API)

1. Install dependencies:

```bash
uv sync --group dev
cd apps/web && npm ci
```

2. Configure API env (`apps/api/.env`) with your local DB/Redis URLs.

3. Run backend:

```bash
uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8080
```

4. Run frontend:

```bash
cd apps/web
npm run dev
```

## Testing

Backend:

```bash
uv run pytest
```

Web:

```bash
cd apps/web
npm run test:run
```

Type checks:

```bash
uv run mypy apps
cd apps/web && npm run typecheck
```

## Deployment Notes

- CI/CD workflows live in `.github/workflows/`.
- EC2 deployment and operational steps are documented in:
  - `docs/deployment-internet-checklist.md`
- Production uses env-file driven Compose (`.env.prod`) for DB and Redis targets.

## Environment Variables

- `DATABASE_WRITE_URL` - primary PostgreSQL endpoint
- `DATABASE_READ_URL` - read replica endpoint (or same as write in local)
- `REDIS_URL` - Redis connection URL

## License

No license file is currently defined in this repository.
