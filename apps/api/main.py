from fastapi import FastAPI, Depends, HTTPException, status, Header, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response
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


app = FastAPI()
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
def get_leaderboard(db: Session = Depends(get_db)) -> LeaderboardResponse:
    rows = get_top_100(db=db)
    entries = [
        LeaderboardEntry(score=row.score, rank=rank + 1, display_name=row.display_name)
        for rank, row in enumerate(rows)
    ]
    return LeaderboardResponse(scores=entries)


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
    return SubmitScoreResponse(score_id=score_id, rank=rank)


@app.get("/health/db", response_model=DBHealthResponse)
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return DBHealthResponse(status="Database connection successful")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
