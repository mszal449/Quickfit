import uuid

from pydantic import BaseModel, ConfigDict, Field

from plan_session.prescription import SessionPrescription


class PlanSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    plan_id: uuid.UUID
    name: str
    prescription: SessionPrescription
    schema_version: int


class PlanSessionCreate(BaseModel):
    name: str
    prescription: SessionPrescription


class PlanSessionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, description="Leave unset to keep as-is")
    prescription: SessionPrescription | None = Field(
        default=None, description="If provided, replaces the session's prescription"
    )
