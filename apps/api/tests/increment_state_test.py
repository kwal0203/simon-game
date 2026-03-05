import pytest

from fastapi.testclient import TestClient
from apps.api.schemas import SubmitScoreRequest
from httpx import Response
from pydantic import ValidationError
from uuid import UUID, uuid4


def test_submit_score_request_requires_non_negative_score() -> None:
    with pytest.raises(ValidationError):
        SubmitScoreRequest(score=-1, display_name="Kane")


@pytest.mark.integration
def test_get_leaderboard(client: TestClient) -> None:
    client.cookies.set("player_id", "22222222-2222-2222-2222-222222222222")
    r: Response = client.get("/v1/leaderboard")
    assert r.status_code == 200
    body = r.json()
    assert "scores" in body
    assert isinstance(body["scores"], list)

    assert [row["score"] for row in body["scores"]] == [84, 75, 35, 12]
    assert [row["rank"] for row in body["scores"]] == [1, 2, 3, 4]
    assert [row["display_name"] for row in body["scores"]] == [
        "Jack",
        "cutok",
        "The lad",
        "Alice",
    ]


@pytest.mark.integration
def test_post_score(client: TestClient) -> None:
    client.cookies.set("player_id", "22222222-2222-2222-2222-222222222222")
    r: Response = client.post(
        "/v1/scores",
        headers={"idempotency-key": "11111111-1111-1111-1111-111111111111"},
        json={"score": 10, "display_name": "Kanos"},
    )

    assert r.status_code == 201
    body = r.json()
    assert "score_id" in body
    UUID(body["score_id"])

    assert "rank" in body
    assert isinstance(body["rank"], int)


@pytest.mark.integration
def test_post_score_rate_limit_returns_429_after_limit(client: TestClient) -> None:
    client.cookies.set("player_id", "22222222-2222-2222-2222-222222222222")
    rate_limited_status_codes: list[int] = []
    for idx in range(13):
        r: Response = client.post(
            "/v1/scores",
            headers={
                "idempotency-key": str(uuid4()),
                "cf-connecting-ip": "198.51.100.42",
            },
            json={"score": 10 + idx, "display_name": "rate-limit-test"},
        )
        rate_limited_status_codes.append(r.status_code)

    assert rate_limited_status_codes[:12] == [201] * 12
    assert rate_limited_status_codes[12] == 429
