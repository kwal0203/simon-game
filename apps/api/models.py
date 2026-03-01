from sqlalchemy import CheckConstraint, UniqueConstraint, Integer, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from datetime import datetime
from .database import Base


class ScoreEntry(Base):
    __tablename__ = "score_entries"
    __table_args__ = (
        UniqueConstraint("idempotency_key", "player_id", name="uq_idempotency_player"),
        CheckConstraint("score >= 0 AND score < 100", name="chk_score_realistic"),
    )

    score_id: Mapped[UUID] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    player_id: Mapped[UUID] = mapped_column(nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
