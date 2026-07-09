import base64
import os
from urllib.parse import urlencode
from uuid import UUID

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from common.exceptions import (
    ConflictError,
    ExternalServiceError,
    NotFoundError,
    UnauthorizedError,
)
from config.service import get_config
from google_health.schema import TokenResponse
from models.integration import Integration, IntegrationProvider

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_HEALTH_API_URL = "https://health.googleapis.com/v4"
NONCE_SIZE = 12

LOG = get_logger()


def build_google_health_url(state: str) -> str:
    cfg = get_config().google_oauth_config
    params = {
        "client_id": cfg.google_client_id,
        "redirect_uri": cfg.google_health_redirect_uri,
        "response_type": "code",
        "scope": " ".join(
            [
                "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
                "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.writeonly",
            ]
        ),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def handle_integration_callback(db: AsyncSession, user_id: UUID, code: str):
    existing = await db.execute(
        select(Integration).where(
            Integration.user_id == user_id,
            Integration.provider == IntegrationProvider.GOOGLE_HEALTH,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("Integration already exists")

    token_res = await exchange_code(code)
    if token_res.refresh_token is None:
        raise ExternalServiceError("Refresh token not received")
    encrypted = encrypt_token(token_res.refresh_token)
    integration = Integration(
        user_id=user_id,
        provider=IntegrationProvider.GOOGLE_HEALTH,
        encrypted_refresh_token=encrypted,
        scope_granted=token_res.scope,
    )
    db.add(integration)
    await db.flush()
    LOG.info("integration_created", integration_id=integration.id, user_id=str(user_id))


async def get_access_token(db: AsyncSession, user_id: UUID) -> str:
    req = await db.execute(select(Integration).where(Integration.user_id == user_id))
    integration = req.scalar_one_or_none()
    if integration is None:
        raise NotFoundError("Integration not found")
    decrypted = decrypt_token(integration.encrypted_refresh_token)

    cfg = get_config().google_oauth_config
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": cfg.google_client_id,
                "client_secret": cfg.google_client_secret,
                "refresh_token": decrypted,
                "grant_type": "refresh_token",
            },
        )
        if resp.status_code == status.HTTP_401_UNAUTHORIZED:
            await db.delete(integration)
            await db.flush()
            raise UnauthorizedError("Grant revoked")
        resp.raise_for_status()
        body = TokenResponse.model_validate(resp.json())
        if body.refresh_token is not None:
            integration.encrypted_refresh_token = encrypt_token(body.refresh_token)
            await db.flush()
        return body.access_token


async def exchange_code(code: str) -> TokenResponse:
    cfg = get_config().google_oauth_config
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": cfg.google_client_id,
                "client_secret": cfg.google_client_secret,
                "redirect_uri": cfg.google_health_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if resp.status_code == status.HTTP_401_UNAUTHORIZED:
            raise UnauthorizedError("Grant revoked")
        resp.raise_for_status()
        body = resp.json()
        return TokenResponse.model_validate(body)


async def revoke_integration(db: AsyncSession, user_id: UUID):
    req = await db.execute(select(Integration).where(Integration.user_id == user_id))
    existing = req.scalar_one_or_none()
    if existing is None:
        raise NotFoundError("Integration not found")
    await db.delete(existing)
    await db.flush()


async def get_integration_status(db: AsyncSession, user_id: UUID) -> Integration | None:
    req = await db.execute(select(Integration).where(Integration.user_id == user_id))
    return req.scalar_one_or_none()


async def read_exercises(db: AsyncSession, user_id: UUID) -> dict:
    token = await get_access_token(db, user_id)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GOOGLE_HEALTH_API_URL}/users/me/dataTypes/exercise/dataPoints",
            headers={"Authorization": f"Bearer {token}"},
            params={"page_size": 10},
        )
        if resp.status_code >= status.HTTP_400_BAD_REQUEST:
            raise ExternalServiceError("Failed to read exercises", extra={"body": resp.text})
        return resp.json()


def encrypt_token(token: str) -> str:
    cfg = get_config()
    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(cfg.integration_secret)
    ciphertext = aesgcm.encrypt(nonce, token.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt_token(token: str) -> str:
    cfg = get_config()
    raw = base64.b64decode(token)
    nonce = raw[:NONCE_SIZE]
    encrypted_token = raw[NONCE_SIZE:]
    aesgcm = AESGCM(cfg.integration_secret)
    return aesgcm.decrypt(nonce, encrypted_token, None).decode()
