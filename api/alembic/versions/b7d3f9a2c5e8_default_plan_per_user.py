"""default_plan_per_user

Revision ID: b7d3f9a2c5e8
Revises: a2c6e8f1d7b4
Create Date: 2026-07-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7d3f9a2c5e8'
down_revision: Union[str, Sequence[str], None] = 'a2c6e8f1d7b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("uq_plans_owner_default", table_name="plans")
    op.drop_column("plans", "is_default")

    op.add_column("users", sa.Column("default_plan_id", sa.UUID(), nullable=True))
    op.create_index(op.f("ix_users_default_plan_id"), "users", ["default_plan_id"], unique=False)
    op.create_foreign_key(
        "fk_users_default_plan_id_plans",
        "users",
        "plans",
        ["default_plan_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_default_plan_id_plans", "users", type_="foreignkey")
    op.drop_index(op.f("ix_users_default_plan_id"), table_name="users")
    op.drop_column("users", "default_plan_id")

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
