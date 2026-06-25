import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from alembic import command
from auth.dependencies import get_current_user_id
from config.db import set_database_engine
from config.middleware import get_db_session
from config.service import get_config
from main import create_app
from models.user import User

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    cfg = Config(str(ALEMBIC_INI))
    command.upgrade(cfg, "head")


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(get_config().db_config.db_url, future=True)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        yield session
        await session.close()
        await trans.rollback()


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    u = User(email=f"user-{uuid.uuid4()}@example.com", is_email_verified=True)
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> User:
    u = User(email=f"other-{uuid.uuid4()}@example.com", is_email_verified=True)
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def app(engine, db_session: AsyncSession) -> FastAPI:
    # override db session for rollbacks
    set_database_engine(engine)
    fastapi_app = create_app()
    fastapi_app.dependency_overrides[get_db_session] = lambda: db_session
    return fastapi_app


@pytest_asyncio.fixture
async def client(app: FastAPI, user: User) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_current_user_id] = lambda: user.id
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
