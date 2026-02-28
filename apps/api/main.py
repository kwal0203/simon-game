from fastapi import FastAPI, status

app = FastAPI()


@app.get("/v1/leaderboard")
def get_leaderboard() -> dict[str, list[int]]:
    return {"scores": []}


@app.post("/v1/scores", status_code=status.HTTP_201_CREATED)
def submit_score() -> dict[str, int]:
    return {"score_response": 99, "rank": 1}
