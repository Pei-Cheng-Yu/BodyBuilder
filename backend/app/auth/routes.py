from app.auth.protected import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .hash import hash_password, verify_password
from .jwt import create_access_token


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=10)
    password: str = Field(min_length=8, max_length=20)
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


router = APIRouter(tags=["auth"])


@router.post("/signup", status_code=201)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=data.username,
        email=data.email,
        password=hash_password(data.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User created", "user_id": str(new_user.id)}


@router.post("/token")
async def login(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.username == form.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    # ⭐ NEW: set HttpOnly cookie for browser + SSE
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # True in HTTPS production
        samesite="lax",  # REQUIRED for SSE
        max_age=60 * 60 * 12,
        path="/",
    )

    # ✅ Keep returning token for non-browser clients (Postman, mobile, etc.)
    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"message": "logged out"}
