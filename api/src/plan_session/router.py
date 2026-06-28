from uuid import UUID

from fastapi import APIRouter, status
from structlog import get_logger

from auth.dependencies import CurrentUserId
from common.schema import Page
from config.middleware import DbSession
from plan_session import service
from plan_session.schema import PlanSessionCreate, PlanSessionOut, PlanSessionUpdate

LOG = get_logger()
router = APIRouter(prefix="/plan/{plan_id}/session", tags=["plan_session"])


@router.get("", response_model=Page[PlanSessionOut])
async def get_sessions(
    plan_id: UUID, user_id: CurrentUserId, db: DbSession
) -> Page[PlanSessionOut]:
    sessions = await service.list_plan_sessions(db, plan_id, user_id)
    return Page[PlanSessionOut](items=sessions, total=len(sessions))


@router.get("/{plan_session_id}", response_model=PlanSessionOut)
async def get_session(
    plan_id: UUID, plan_session_id: UUID, user_id: CurrentUserId, db: DbSession
) -> PlanSessionOut:
    return await service.get_plan_session(db, plan_id, plan_session_id, user_id)


@router.post("", response_model=PlanSessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    plan_id: UUID, payload: PlanSessionCreate, user_id: CurrentUserId, db: DbSession
) -> PlanSessionOut:
    return await service.create_plan_session(db, plan_id, user_id, payload)


@router.patch("/{plan_session_id}", response_model=PlanSessionOut)
async def update_session(
    plan_id: UUID,
    plan_session_id: UUID,
    payload: PlanSessionUpdate,
    user_id: CurrentUserId,
    db: DbSession,
) -> PlanSessionOut:
    return await service.update_plan_session(db, plan_id, plan_session_id, user_id, payload)


@router.delete("/{plan_session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    plan_id: UUID, plan_session_id: UUID, user_id: CurrentUserId, db: DbSession
) -> None:
    return await service.delete_plan_session(db, plan_id, plan_session_id, user_id)
