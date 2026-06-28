"""add_category_and_muscle_group_to_exercise

Revision ID: b2886fc73782
Revises: a994fe8f8cb5
Create Date: 2026-06-28 11:35:10.325133

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2886fc73782'
down_revision: Union[str, Sequence[str], None] = 'a994fe8f8cb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    exercise_category = sa.Enum("strength", "cardio", name="exercisecategory")
    muscle_group = sa.Enum(
        "chest", "back", "shoulders", "biceps", "triceps", "forearms", "core",
        "quads", "hamstrings", "glutes", "calves", "full_body", name="musclegroup",
    )
    exercise_category.create(op.get_bind(), checkfirst=True)
    muscle_group.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "exercises",
        sa.Column("category", exercise_category, nullable=False, server_default="strength"),
    )
    op.add_column("exercises", sa.Column("muscle_group", muscle_group, nullable=True))
    op.alter_column("exercises", "category", server_default=None)


def downgrade() -> None:
    op.drop_column("exercises", "muscle_group")
    op.drop_column("exercises", "category")
    sa.Enum(name="musclegroup").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="exercisecategory").drop(op.get_bind(), checkfirst=True)
