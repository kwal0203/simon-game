"""score_entries

Revision ID: 9fb319784f10
Revises:
Create Date: 2026-02-28 19:23:09.555574

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9fb319784f10"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "score_entries",
        sa.Column("score_id", sa.UUID(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("score_id"),
        sa.UniqueConstraint(
            "idempotency_key", "player_id", name="uq_idempotency_player"
        ),
        sa.CheckConstraint("score >= 0 AND score < 100", name="chk_score_realistic"),
    )

    op.create_index(
        "ix_score_entries_score_created",
        "score_entries",
        [sa.text("score DESC"), sa.text("created_at DESC")],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_score_entries_score_created", table_name="score_entries")
    op.drop_table("score_entries")
