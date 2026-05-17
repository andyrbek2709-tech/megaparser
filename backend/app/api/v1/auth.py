from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from app.api.deps import DB, CurrentUser
from app.config import settings
from app.models.user import User
from app.schemas.user import TokenRefresh, TokenResponse, UserCreate, UserLogin, UserResponse
from sqlalchemy import select

logger = structlog.get_logger()
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(user_id: str, expire_minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.SECRET_KEY, algorithm="HS256")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: DB) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail={"code": "EMAIL_EXISTS", "message": "Email already registered"})
    user = User(email=data.email, password_hash=pwd_context.hash(data.password))
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: DB) -> dict:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"})
    if not user.is_active:
        raise HTTPException(status_code=403, detail={"code": "INACTIVE", "message": "Account is inactive"})
    return {
        "access_token": create_token(str(user.id), settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "refresh_token": create_token(str(user.id), settings.ACCESS_TOKEN_EXPIRE_MINUTES * 7),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: TokenRefresh, db: DB) -> dict:
    from jose import JWTError
    try:
        payload = jwt.decode(data.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Invalid refresh token"})
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail={"code": "USER_NOT_FOUND", "message": "User not found"})
    return {
        "access_token": create_token(str(user.id), settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "refresh_token": create_token(str(user.id), settings.ACCESS_TOKEN_EXPIRE_MINUTES * 7),
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(current_user: CurrentUser) -> dict:
    return {"message": "Logged out successfully"}
