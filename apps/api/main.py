from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from .database import get_db

app = FastAPI()


@app.get("/v1/leaderboard")
def get_leaderboard() -> dict[str, list[int]]:
    return {"scores": []}


@app.post("/v1/scores", status_code=status.HTTP_201_CREATED)
def submit_score() -> dict[str, int]:
    return {"score_response": 99, "rank": 1}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
