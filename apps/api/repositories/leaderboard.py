from sqlalchemy.orm import Session
from sqlalchemy import select
from apps.api.models import ScoreEntry


def get_top_100(db: Session) -> list[ScoreEntry]:
    stmt = (
        select(ScoreEntry)
        .order_by(ScoreEntry.score.desc(), ScoreEntry.created_at.desc())
        .limit(100)
    )

    return list(db.scalars(stmt).all())
