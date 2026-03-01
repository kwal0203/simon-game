from pydantic import BaseModel, Field
from uuid import UUID


class LeaderboardEntry(BaseModel):
    score: int
    rank: int
    display_name: str


class LeaderboardResponse(BaseModel):
    scores: list[LeaderboardEntry]


class SubmitScoreResponse(BaseModel):
    score_id: UUID
    rank: int


class SubmitScoreRequest(BaseModel):
    score: int = Field(ge=0)
    display_name: str = Field(min_length=1, max_length=16)


class DBHealthResponse(BaseModel):
    status: str
