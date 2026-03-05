import pytest

from datetime import datetime
from sqlalchemy import text
from apps.api.database import SessionLocal
from uuid import UUID
from collections.abc import Iterator
from fastapi.testclient import TestClient
from apps.api.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_score_entries(request: pytest.FixtureRequest) -> Iterator[None]:
    if "integration" not in request.keywords:
        yield
        return

    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE TABLE score_entries;"))
        db.execute(
            text(
                """
                INSERT INTO score_entries
                    (score_id, score, player_id, idempotency_key, created_at, display_name)
                VALUES
                    (:score_id_1, :score_1, :player_id_1, :idempotency_key_1, :created_at_1, :display_name_1),
                    (:score_id_2, :score_2, :player_id_2, :idempotency_key_2, :created_at_2, :display_name_2),
                    (:score_id_3, :score_3, :player_id_3, :idempotency_key_3, :created_at_3, :display_name_3),
                    (:score_id_4, :score_4, :player_id_4, :idempotency_key_4, :created_at_4, :display_name_4)
                """
            ),
            {
                "score_id_1": UUID("ff257b4a-34ed-4b41-b2af-d828a3fc1910"),
                "score_1": 84,
                "player_id_1": UUID("6b3f82fe-8391-441e-9418-fe61ba33d78c"),
                "idempotency_key_1": UUID("1afe7c78-4e6e-4345-b6bc-24ad709a1d30"),
                "created_at_1": datetime.fromisoformat("2026-03-01T04:38:13.668148"),
                "display_name_1": "Jack",
                "score_id_2": UUID("61b2a24a-ddda-4b33-8ba4-34309316028a"),
                "score_2": 75,
                "player_id_2": UUID("e0754a51-8b0d-4d47-9fac-d593ae4ec3f2"),
                "idempotency_key_2": UUID("ccaef863-3ca5-4e18-8274-17f4b9059725"),
                "created_at_2": datetime.fromisoformat("2026-03-01T04:38:13.667777"),
                "display_name_2": "cutok",
                "score_id_3": UUID("120b08a5-06c5-474f-ae2d-f21cdd102167"),
                "score_3": 35,
                "player_id_3": UUID("eb3fae3d-7479-43a6-b3b3-f61291c7668b"),
                "idempotency_key_3": UUID("c534e4d9-09b3-42aa-9c3a-b86768079c6e"),
                "created_at_3": datetime.fromisoformat("2026-03-01T04:38:13.666659"),
                "display_name_3": "The lad",
                "score_id_4": UUID("4a091f64-42be-4071-b688-7a8771b8d96e"),
                "score_4": 12,
                "player_id_4": UUID("dd2cf649-cc27-4fc2-a2db-2d7845b5df6e"),
                "idempotency_key_4": UUID("6caa08e9-f85d-4aff-8533-0fa54d6889d5"),
                "created_at_4": datetime.fromisoformat("2026-03-01T04:38:13.667282"),
                "display_name_4": "Alice",
            },
        )

        db.commit()
        yield
    finally:
        db.close()
