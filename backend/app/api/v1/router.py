from fastapi import APIRouter

from app.api.v1 import auth, accounts, posts, generation, analytics, strategy

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(generation.router, prefix="/generation", tags=["generation"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(strategy.router, prefix="/strategy", tags=["strategy"])
