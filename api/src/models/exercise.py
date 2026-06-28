import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from models.model_base import BaseModel


class ExerciseCategory(enum.StrEnum):
    STRENGTH = "strength"
    CARDIO = "cardio"


class MuscleGroup(enum.StrEnum):
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    FOREARMS = "forearms"
    CORE = "core"
    QUADS = "quads"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    FULL_BODY = "full_body"


class Exercise(BaseModel):
    __tablename__ = "exercises"
    __table_args__ = (
        Index(
            "uq_exercises_owner_name_active",
            "owner_id",
            "name",
            unique=True,
            postgresql_where=text("is_archived = false"),
        ),
    )

    # NULL = global exercise
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[ExerciseCategory] = mapped_column(
        SAEnum(ExerciseCategory), default=ExerciseCategory.STRENGTH
    )
    # NULL for cardio exercises, which don't have a single primary muscle group.
    muscle_group: Mapped[MuscleGroup | None] = mapped_column(SAEnum(MuscleGroup), nullable=True)

    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
