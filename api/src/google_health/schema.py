from datetime import datetime

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    scope: str
    expires_in: int
    token_type: str


class IntegrationStatusOut(BaseModel):
    connected: bool
    scope_granted: str | None = None
    created_at: datetime | None = None
