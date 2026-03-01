import uuid
import random

from sqlalchemy import text
from datetime import datetime, timezone
from apps.api.database import engine


def run_seed():
    names = ["The lad", "Alice", "cutok", "Jack"]

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE score_entries;"))
        for name in names:
            score = random.randint(10, 100)
            conn.execute(
                text("""
                    INSERT INTO score_entries (
                        score_id, score, player_id, idempotency_key, created_at, display_name
                    ) VALUES (
                        :score_id, :score, :player_id, :idempotency_key, :created_at, :display_name
                    )
                """),
                {
                    "score_id": str(uuid.uuid4()),
                    "score": score,
                    "player_id": str(uuid.uuid4()),
                    "idempotency_key": str(uuid.uuid4()),
                    "created_at": datetime.now(timezone.utc),
                    "display_name": name,
                },
            )

    print("Successfully seeded the leaderboard with test data.")


if __name__ == "__main__":
    run_seed()
