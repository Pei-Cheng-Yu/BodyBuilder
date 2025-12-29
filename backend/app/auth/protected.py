from app.auth.jwt import decode_access_token
from app.db.models.user import User
from app.db.session import get_db
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def extract_token(request: Request) -> str | None:
    # 1️⃣ Cookie-based JWT (preferred, works with SSE)
    token = request.cookies.get("access_token")
    if token:
        return token

    # 2️⃣ Header-based JWT (fallback)
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[len("Bearer ") :]

    return None


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    token = extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
