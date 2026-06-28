"""fix_exercise_enum_label_casing

Revision ID: c97285a25f9f
Revises: b2886fc73782
Create Date: 2026-06-28 11:50:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c97285a25f9f'
down_revision: Union[str, Sequence[str], None] = 'b2886fc73782'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CATEGORY_LABELS = [("strength", "STRENGTH"), ("cardio", "CARDIO")]
_MUSCLE_GROUP_LABELS = [
    ("chest", "CHEST"),
    ("back", "BACK"),
    ("shoulders", "SHOULDERS"),
    ("biceps", "BICEPS"),
    ("triceps", "TRICEPS"),
    ("forearms", "FOREARMS"),
    ("core", "CORE"),
    ("quads", "QUADS"),
    ("hamstrings", "HAMSTRINGS"),
    ("glutes", "GLUTES"),
    ("calves", "CALVES"),
    ("full_body", "FULL_BODY"),
]


def upgrade() -> None:
    for old, new in _CATEGORY_LABELS:
        op.execute(f"ALTER TYPE exercisecategory RENAME VALUE '{old}' TO '{new}'")
    for old, new in _MUSCLE_GROUP_LABELS:
        op.execute(f"ALTER TYPE musclegroup RENAME VALUE '{old}' TO '{new}'")


def downgrade() -> None:
    for old, new in _CATEGORY_LABELS:
        op.execute(f"ALTER TYPE exercisecategory RENAME VALUE '{new}' TO '{old}'")
    for old, new in _MUSCLE_GROUP_LABELS:
        op.execute(f"ALTER TYPE musclegroup RENAME VALUE '{new}' TO '{old}'")
