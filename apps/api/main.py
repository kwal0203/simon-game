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
from uuid import UUID, uuid4

app = FastAPI()


@app.get("/v1/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard() -> LeaderboardResponse:
    return LeaderboardResponse(
        scores=[LeaderboardEntry(score=10, rank=1, display_name="Kanos")]
    )


@app.post(
    "/v1/scores",
    status_code=status.HTTP_201_CREATED,
    response_model=SubmitScoreResponse,
)
def submit_score(
    payload: SubmitScoreRequest,
    idempotency_key: UUID = Header(...),
    player_id: UUID = Cookie(...),
) -> SubmitScoreResponse:
    return SubmitScoreResponse(score_id=uuid4(), rank=1)


@app.get("/health/db", response_model=DBHealthResponse)
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return DBHealthResponse(status="Database connection successful")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
