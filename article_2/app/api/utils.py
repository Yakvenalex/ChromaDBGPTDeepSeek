import json
from datetime import datetime, timedelta
from typing import Optional

import aiofiles
import jwt
from fastapi import Cookie, HTTPException

from app.config import settings


async def get_all_users():
    async with aiofiles.open(settings.USERS) as f:
        content = await f.read()
        users = json.loads(content)
        return users


async def authenticate_user(login: str, password: str):
    users = await get_all_users()
    for user in users:
        if user["login"] == login and user["password"] == password:
            return user
    return None


async def create_jwt_token(user_id: int):
    expire = datetime.now() + timedelta(hours=1)
    payload = {
        "sub": str(user_id),
        "exp": expire.timestamp(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


async def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    access_token: Optional[str] = Cookie(default=None),
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing token")
    user_id = await verify_jwt_token(access_token)
    return user_id


async def get_optional_current_user(
    access_token: Optional[str] = Cookie(default=None),
) -> Optional[int]:
    if not access_token:
        return None
    try:
        user_id = await verify_jwt_token(access_token)
        return user_id
    except Exception:
        return None
