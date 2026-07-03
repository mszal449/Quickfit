"""add_is_default_to_plans

Revision ID: a2c6e8f1d7b4
Revises: f4a7c1e9b3d2
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2c6e8f1d7b4'
down_revision: Union[str, Sequence[str], None] = 'f4a7c1e9b3d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "plans",
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("plans", "is_default", server_default=None)
    op.create_index(
        "uq_plans_owner_default",
        "plans",
        ["owner_id"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )


def downgrade() -> None:
    op.drop_index("uq_plans_owner_default", table_name="plans")
    op.drop_column("plans", "is_default")
