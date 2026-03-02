from fastapi import FastAPI, Depends, HTTPException, status, Header, Cookie
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
from apps.api.repositories.leaderboard import get_top_100, insert_score_entry

app = FastAPI()


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
def submit_score(
    payload: SubmitScoreRequest,
    idempotency_key: UUID = Header(...),
    player_id: UUID = Cookie(...),
    db: Session = Depends(get_db),
) -> SubmitScoreResponse:
    score_id, rank = insert_score_entry(
        db=db,
        score=payload.score,
        player_id=player_id,
        idempotency_key=idempotency_key,
        display_name=payload.display_name,
    )
    return SubmitScoreResponse(score_id=score_id, rank=rank)


@app.get("/health/db", response_model=DBHealthResponse)
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return DBHealthResponse(status="Database connection successful")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
