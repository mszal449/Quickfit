"""add_updated_at_and_name_unique_constraint_on_plan_shares

Revision ID: f4a7c1e9b3d2
Revises: e18f2ad934bc
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4a7c1e9b3d2'
down_revision: Union[str, Sequence[str], None] = 'e18f2ad934bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "plan_shares",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.alter_column("plan_shares", "updated_at", server_default=None)
    op.drop_constraint(
        "plan_shares_plan_id_shared_with_user_id_key", "plan_shares", type_="unique"
    )
    op.create_unique_constraint(
        "uq_plan_shares_plan_id_shared_with_user_id",
        "plan_shares",
        ["plan_id", "shared_with_user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_plan_shares_plan_id_shared_with_user_id", "plan_shares", type_="unique"
    )
    op.create_unique_constraint(
        "plan_shares_plan_id_shared_with_user_id_key",
        "plan_shares",
        ["plan_id", "shared_with_user_id"],
    )
    op.drop_column("plan_shares", "updated_at")
