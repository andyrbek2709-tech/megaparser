import uuid

import structlog
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import DB, CurrentUser
from app.config import settings
from app.models.social_account import SocialAccount
from app.services.social.instagram import InstagramClient

logger = structlog.get_logger()
router = APIRouter()
instagram_client = InstagramClient()


class AccountResponse(BaseModel):
    id: uuid.UUID
    platform: str
    username: str | None
    account_type: str | None
    is_active: bool
    token_expires_at: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[AccountResponse])
async def list_accounts(current_user: CurrentUser, db: DB) -> list[SocialAccount]:
    result = await db.execute(
        select(SocialAccount).where(SocialAccount.user_id == current_user.id, SocialAccount.is_active == True)
    )
    return list(result.scalars().all())


@router.post("/instagram/connect")
async def instagram_connect(current_user: CurrentUser) -> dict:
    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={settings.INSTAGRAM_APP_ID}"
        f"&redirect_uri={settings.INSTAGRAM_REDIRECT_URI}"
        f"&scope=instagram_basic,instagram_content_publish,instagram_manage_insights"
        f"&response_type=code"
        f"&state={current_user.id}"
    )
    return {"auth_url": auth_url}


@router.get("/instagram/callback")
async def instagram_callback(code: str, state: str, db: DB) -> dict:
    try:
        token_data = await instagram_client.exchange_code_for_token(code, settings.INSTAGRAM_REDIRECT_URI)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code": "OAUTH_FAILED", "message": str(e)})

    from app.services.security import encrypt_token
    account = SocialAccount(
        user_id=uuid.UUID(state),
        platform="instagram",
        platform_user_id=token_data["user_id"],
        username=token_data.get("username"),
        access_token=encrypt_token(token_data["access_token"]),
        account_type=token_data.get("account_type", "business"),
        token_expires_at=token_data.get("expires_at"),
    )
    db.add(account)
    await db.flush()
    return {"message": "Instagram account connected", "account_id": str(account.id)}


@router.delete("/{account_id}", status_code=204)
async def disconnect_account(account_id: uuid.UUID, current_user: CurrentUser, db: DB) -> None:
    result = await db.execute(
        select(SocialAccount).where(SocialAccount.id == account_id, SocialAccount.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Account not found"})
    account.is_active = False


@router.get("/{account_id}/status")
async def account_status(account_id: uuid.UUID, current_user: CurrentUser, db: DB) -> dict:
    result = await db.execute(
        select(SocialAccount).where(SocialAccount.id == account_id, SocialAccount.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Account not found"})
    return {
        "id": str(account.id),
        "platform": account.platform,
        "is_active": account.is_active,
        "token_expires_at": account.token_expires_at.isoformat() if account.token_expires_at else None,
    }
