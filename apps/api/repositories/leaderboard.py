from sqlalchemy.orm import Session
from sqlalchemy import select, func
from apps.api.models import ScoreEntry
from uuid import UUID, uuid4
from datetime import datetime, UTC


def get_top_100(db: Session) -> list[ScoreEntry]:
    stmt = (
        select(ScoreEntry)
        .order_by(ScoreEntry.score.desc(), ScoreEntry.created_at.desc())
        .limit(100)
    )

    return list(db.scalars(stmt).all())


def insert_score_entry(
    db: Session, score: int, player_id: UUID, idempotency_key: UUID, display_name: str
) -> tuple[UUID, int]:
    row = ScoreEntry(
        score_id=uuid4(),
        score=score,
        player_id=player_id,
        idempotency_key=idempotency_key,
        created_at=datetime.now(UTC),
        display_name=display_name,
    )

    try:
        db.add(row)
        db.flush()

        ranked = select(
            ScoreEntry.score_id,
            func.row_number()
            .over(order_by=(ScoreEntry.score.desc(), ScoreEntry.created_at.desc()))
            .label("rank"),
        ).subquery()

        rank_stmt = select(ranked.c.rank).where(ranked.c.score_id == row.score_id)
        rank = db.execute(rank_stmt).scalar_one()

        db.commit()
        return row.score_id, int(rank)
    except Exception:
        db.rollback()
        raise
