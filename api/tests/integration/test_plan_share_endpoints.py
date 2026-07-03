import uuid

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.friendship import Friendship, FriendshipStatus
from models.plan import Plan
from models.plan_share import PlanShare, PlanShareStatus
from models.user import User
from models.workout_log import WorkoutLog


async def _make_friends(db_session: AsyncSession, user: User, other_user: User) -> None:
    db_session.add(
        Friendship(
            requester_id=user.id, addressee_id=other_user.id, status=FriendshipStatus.ACCEPTED
        )
    )
    await db_session.flush()


async def _make_plan(db_session: AsyncSession, owner: User) -> Plan:
    plan = Plan(owner_id=owner.id, name="Strength block", description=None)
    db_session.add(plan)
    await db_session.flush()
    return plan


async def test_create_plan_share(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    await _make_friends(db_session, user, other_user)
    plan = await _make_plan(db_session, user)

    resp = await client.post(
        "/api/plan-share",
        json={"plan_id": str(plan.id), "shared_with_user_id": str(other_user.id)},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["plan_id"] == str(plan.id)
    assert body["owner_id"] == str(user.id)
    assert body["status"] == PlanShareStatus.PENDING.value
    assert body["user"]["email"] == other_user.email


async def test_create_plan_share_requires_ownership(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    await _make_friends(db_session, user, other_user)
    plan = await _make_plan(db_session, other_user)

    resp = await client.post(
        "/api/plan-share",
        json={"plan_id": str(plan.id), "shared_with_user_id": str(other_user.id)},
    )
    assert resp.status_code == 404


async def test_create_plan_share_requires_friendship(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, user)

    resp = await client.post(
        "/api/plan-share",
        json={"plan_id": str(plan.id), "shared_with_user_id": str(other_user.id)},
    )
    assert resp.status_code == 403


async def test_create_plan_share_to_self_is_rejected(
    client: AsyncClient, db_session: AsyncSession, user: User
):
    plan = await _make_plan(db_session, user)

    resp = await client.post(
        "/api/plan-share",
        json={"plan_id": str(plan.id), "shared_with_user_id": str(user.id)},
    )
    assert resp.status_code == 409


async def test_create_duplicate_plan_share_is_rejected(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    await _make_friends(db_session, user, other_user)
    plan = await _make_plan(db_session, user)
    db_session.add(PlanShare(plan_id=plan.id, owner_id=user.id, shared_with_user_id=other_user.id))
    await db_session.flush()

    resp = await client.post(
        "/api/plan-share",
        json={"plan_id": str(plan.id), "shared_with_user_id": str(other_user.id)},
    )
    assert resp.status_code == 409


async def test_recreate_after_revoke_reactivates_share(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    await _make_friends(db_session, user, other_user)
    plan = await _make_plan(db_session, user)
    share = PlanShare(
        plan_id=plan.id,
        owner_id=user.id,
        shared_with_user_id=other_user.id,
        status=PlanShareStatus.REVOKED,
    )
    db_session.add(share)
    await db_session.flush()
    share_id = share.id

    resp = await client.post(
        "/api/plan-share",
        json={"plan_id": str(plan.id), "shared_with_user_id": str(other_user.id)},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == str(share_id)
    assert body["status"] == PlanShareStatus.PENDING.value


async def test_accept_plan_share(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, other_user)
    share = PlanShare(plan_id=plan.id, owner_id=other_user.id, shared_with_user_id=user.id)
    db_session.add(share)
    await db_session.flush()

    resp = await client.post(f"/api/plan-share/{share.id}/accept")

    assert resp.status_code == 200
    assert resp.json()["status"] == PlanShareStatus.ACCEPTED.value


async def test_accept_plan_share_by_owner_is_forbidden(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, user)
    share = PlanShare(plan_id=plan.id, owner_id=user.id, shared_with_user_id=other_user.id)
    db_session.add(share)
    await db_session.flush()

    resp = await client.post(f"/api/plan-share/{share.id}/accept")
    assert resp.status_code == 403


async def test_revoke_plan_share(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, user)
    share = PlanShare(
        plan_id=plan.id,
        owner_id=user.id,
        shared_with_user_id=other_user.id,
        status=PlanShareStatus.ACCEPTED,
    )
    db_session.add(share)
    await db_session.flush()

    resp = await client.post(f"/api/plan-share/{share.id}/revoke")

    assert resp.status_code == 200
    assert resp.json()["status"] == PlanShareStatus.REVOKED.value


async def test_revoke_pending_share_is_conflict(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, user)
    share = PlanShare(plan_id=plan.id, owner_id=user.id, shared_with_user_id=other_user.id)
    db_session.add(share)
    await db_session.flush()

    resp = await client.post(f"/api/plan-share/{share.id}/revoke")
    assert resp.status_code == 409


async def test_revoke_by_recipient_is_forbidden(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, other_user)
    share = PlanShare(
        plan_id=plan.id,
        owner_id=other_user.id,
        shared_with_user_id=user.id,
        status=PlanShareStatus.ACCEPTED,
    )
    db_session.add(share)
    await db_session.flush()

    resp = await client.post(f"/api/plan-share/{share.id}/revoke")
    assert resp.status_code == 403


async def test_remove_pending_plan_share(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, user)
    share = PlanShare(plan_id=plan.id, owner_id=user.id, shared_with_user_id=other_user.id)
    db_session.add(share)
    await db_session.flush()

    resp = await client.delete(f"/api/plan-share/{share.id}")
    assert resp.status_code == 204


async def test_remove_accepted_plan_share_is_conflict(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, user)
    share = PlanShare(
        plan_id=plan.id,
        owner_id=user.id,
        shared_with_user_id=other_user.id,
        status=PlanShareStatus.ACCEPTED,
    )
    db_session.add(share)
    await db_session.flush()

    resp = await client.delete(f"/api/plan-share/{share.id}")
    assert resp.status_code == 409


async def test_recipient_can_leave_accepted_plan_share(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, other_user)
    share = PlanShare(
        plan_id=plan.id,
        owner_id=other_user.id,
        shared_with_user_id=user.id,
        status=PlanShareStatus.ACCEPTED,
    )
    db_session.add(share)
    await db_session.flush()

    resp = await client.delete(f"/api/plan-share/{share.id}")
    assert resp.status_code == 204


async def test_remove_plan_share_unrelated_user_returns_not_found(
    client: AsyncClient, db_session: AsyncSession, other_user: User
):
    third_party = User(email=f"third-{uuid.uuid4()}@example.com", is_email_verified=True)
    db_session.add(third_party)
    await db_session.flush()
    plan = await _make_plan(db_session, other_user)
    share = PlanShare(plan_id=plan.id, owner_id=other_user.id, shared_with_user_id=third_party.id)
    db_session.add(share)
    await db_session.flush()

    resp = await client.delete(f"/api/plan-share/{share.id}")
    assert resp.status_code == 404


async def test_get_share_progress(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, user)
    share = PlanShare(
        plan_id=plan.id,
        owner_id=user.id,
        shared_with_user_id=other_user.id,
        status=PlanShareStatus.ACCEPTED,
    )
    db_session.add(share)
    db_session.add(WorkoutLog(user_id=other_user.id, plan_id=plan.id))
    await db_session.flush()

    resp = await client.get(f"/api/plan-share/{share.id}/progress")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["user_id"] == str(other_user.id)


async def test_get_share_progress_requires_accepted(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, user)
    share = PlanShare(plan_id=plan.id, owner_id=user.id, shared_with_user_id=other_user.id)
    db_session.add(share)
    await db_session.flush()

    resp = await client.get(f"/api/plan-share/{share.id}/progress")
    assert resp.status_code == 409


async def test_get_share_progress_by_non_owner_returns_not_found(
    client: AsyncClient, db_session: AsyncSession, user: User, other_user: User
):
    plan = await _make_plan(db_session, other_user)
    share = PlanShare(
        plan_id=plan.id,
        owner_id=other_user.id,
        shared_with_user_id=user.id,
        status=PlanShareStatus.ACCEPTED,
    )
    db_session.add(share)
    await db_session.flush()

    resp = await client.get(f"/api/plan-share/{share.id}/progress")
    assert resp.status_code == 404


async def test_plan_share_endpoints_require_auth(app: FastAPI):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/plan-share")
    assert resp.status_code == 401
