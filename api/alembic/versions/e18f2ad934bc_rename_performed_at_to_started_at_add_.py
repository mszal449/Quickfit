"""rename_performed_at_to_started_at_add_completed_at

Revision ID: e18f2ad934bc
Revises: 9c1f4a7d3e6b
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e18f2ad934bc'
down_revision: Union[str, Sequence[str], None] = '9c1f4a7d3e6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "workout_logs",
        "performed_at",
        new_column_name="started_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.execute("ALTER INDEX ix_workout_logs_performed_at RENAME TO ix_workout_logs_started_at")
    op.add_column(
        "workout_logs", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.execute("UPDATE workout_logs SET completed_at = started_at WHERE status = 'COMPLETED'")


def downgrade() -> None:
    op.drop_column("workout_logs", "completed_at")
    op.execute("ALTER INDEX ix_workout_logs_started_at RENAME TO ix_workout_logs_performed_at")
    op.alter_column(
        "workout_logs",
        "started_at",
        new_column_name="performed_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
