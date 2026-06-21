from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from auth.security import decode_access_token
from config.middleware import DbSession
from models.user import User, UserRole


async def get_current_user(req: Request, db: DbSession) -> User:
    token = req.cookies.get("access_token")
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    payload = decode_access_token(token)
    user = await User.get(db, payload.sub)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return user


def require_role(role: UserRole):
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
        return user
    return checker


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_role(UserRole.ADMIN))]