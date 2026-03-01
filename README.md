# Simon Game

Web-based version of the Simon Game.

## Overview
This repository contains:
- A FastAPI backend (`apps/api`) for game/leaderboard endpoints
- A web app workspace (`apps/web`) with TypeScript game logic tests
- PostgreSQL migration and seed scaffolding (`database`)

## Project Structure
- `apps/api` - FastAPI application
- `apps/web` - Web client code and tests
- `database/migrations` - Alembic migration environment and revision files
- `database/seeds` - Seed scripts for local/dev data
- `docs` - Technical and operational docs

## Prerequisites
- Python 3.12+
- `uv` package manager
- PostgreSQL (local or Docker)

## Backend Setup
1. Install Python dependencies:
```bash
uv sync
```

2. Create environment file for API settings:
```bash
cp apps/api/.env.example apps/api/.env
```

3. Set `DATABASE_URL` in `apps/api/.env`.

4. Run migrations:
```bash
uv run alembic upgrade head
```

5. Start the API:
```bash
uv run uvicorn apps.api.main:app --reload
```

API will be available at `http://127.0.0.1:8000`.

## Useful Endpoints
- `GET /v1/leaderboard`
- `POST /v1/scores`
- `GET /health/db`

## Tests
Backend tests:
```bash
uv run pytest
```

Web tests:
```bash
cd apps/web
npm test
```

## Notes
- Keep secrets in `apps/api/.env` (do not commit this file).
- Commit migration source files in `database/migrations/versions`.
- Do not commit `__pycache__` or `*.pyc` files.
