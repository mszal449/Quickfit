from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from auth.dependencies import CurrentUserId
from common.schema import Page
from config.middleware import DbSession
from plan_share import service
from plan_share.schema import PlanShareCreate, PlanShareFilterParams, PlanShareOut
from workout_log.schema import WorkoutLogOut

router = APIRouter(prefix="/plan-share", tags=["plan_share"])


@router.get("", response_model=Page[PlanShareOut])
async def get_plan_shares(
    user_id: CurrentUserId,
    filters: Annotated[PlanShareFilterParams, Query()],
    db: DbSession,
) -> Page[PlanShareOut]:
    shares = await service.list_plan_shares(db, user_id, filters)
    return Page[PlanShareOut](items=shares, total=len(shares))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PlanShareOut)
async def create_plan_share(
    user_id: CurrentUserId, payload: PlanShareCreate, db: DbSession
) -> PlanShareOut:
    return await service.create_plan_share(db, user_id, payload)


@router.post("/{plan_share_id}/accept", response_model=PlanShareOut)
async def accept_plan_share(
    user_id: CurrentUserId, plan_share_id: UUID, db: DbSession
) -> PlanShareOut:
    return await service.accept_plan_share(db, user_id, plan_share_id)


@router.post("/{plan_share_id}/revoke", response_model=PlanShareOut)
async def revoke_plan_share(
    user_id: CurrentUserId, plan_share_id: UUID, db: DbSession
) -> PlanShareOut:
    return await service.revoke_plan_share(db, user_id, plan_share_id)


@router.delete("/{plan_share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_plan_share(user_id: CurrentUserId, plan_share_id: UUID, db: DbSession) -> None:
    return await service.remove_plan_share(db, user_id, plan_share_id)


@router.get("/{plan_share_id}/progress", response_model=Page[WorkoutLogOut])
async def get_share_progress(
    user_id: CurrentUserId, plan_share_id: UUID, db: DbSession
) -> Page[WorkoutLogOut]:
    logs = await service.get_share_progress(db, user_id, plan_share_id)
    return Page[WorkoutLogOut](items=logs, total=len(logs))
