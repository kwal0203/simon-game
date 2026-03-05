from apps.api.settings import init_settings
from fastapi import FastAPI, Depends, HTTPException, status, Header, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.orm import Session
from .database import get_db
from .schemas import (
    LeaderboardResponse,
    SubmitScoreResponse,
    SubmitScoreRequest,
    DBHealthResponse,
    LeaderboardEntry,
)
from uuid import UUID
from apps.api.repositories.leaderboard import (
    get_top_100,
    insert_score_entry,
    DuplicateScoreSubmissionError,
)
from redis import Redis

import redis
import os

init_settings()


def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip

    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


def rate_limit_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    raise exc


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    redis_client: Redis = redis.from_url(redis_url, decode_responses=True)
    app.state.redis = redis_client

    try:
        redis_client.ping()  # type: ignore[no-untyped-call]
    except Exception:
        app.state.redis = None

    try:
        yield
    finally:
        if app.state.redis is not None:
            app.state.redis.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_client_ip)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


@app.get("/v1/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    request: Request, db: Session = Depends(get_db)
) -> LeaderboardResponse:
    cache_key = "leaderboard:top100"
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        cached = redis_client.get(cache_key)
        if cached:
            return LeaderboardResponse.model_validate_json(cached)

    rows = get_top_100(db=db)
    entries = [
        LeaderboardEntry(score=row.score, rank=rank + 1, display_name=row.display_name)
        for rank, row in enumerate(rows)
    ]
    response = LeaderboardResponse(scores=entries)

    if redis_client is not None:
        redis_client.set(cache_key, response.model_dump_json(), ex=10)

    return response


@app.post(
    "/v1/scores",
    status_code=status.HTTP_201_CREATED,
    response_model=SubmitScoreResponse,
)
@limiter.limit(  # type: ignore[misc]
    "12/minute"
)
def submit_score(
    request: Request,
    payload: SubmitScoreRequest,
    idempotency_key: UUID = Header(...),
    player_id: UUID = Cookie(...),
    db: Session = Depends(get_db),
) -> SubmitScoreResponse:
    try:
        score_id, rank = insert_score_entry(
            db=db,
            score=payload.score,
            player_id=player_id,
            idempotency_key=idempotency_key,
            display_name=payload.display_name,
        )
    except DuplicateScoreSubmissionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Duplicate score submission."
        )

    cache_key = "leaderboard:top100"
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        redis_client.delete(cache_key)

    return SubmitScoreResponse(score_id=score_id, rank=rank)


@app.get("/health/db", response_model=DBHealthResponse)
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return DBHealthResponse(status="Database connection successful")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
