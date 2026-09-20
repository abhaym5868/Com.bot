"""
routes/analytics.py
--------------------
Admin analytics endpoints:
- GET /api/v1/analytics/dashboard  — aggregate dashboard stats
- GET /api/v1/analytics/updates    — per-update performance
- POST /api/v1/analytics/view/{changelog_id} — record a view (public)
"""

from fastapi import APIRouter, Depends, Query, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.middleware.auth import get_current_admin_user, get_optional_current_user
from app.models.user import UserModel
from app.services import analytics_service

router = APIRouter()


@router.get(
    "/dashboard",
    summary="Admin analytics dashboard stats (Admin only)",
    description="Returns aggregated totals: views, reactions, published/draft counts, top performers.",
)
async def analytics_dashboard(
    admin_user: UserModel = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await analytics_service.get_dashboard_stats(db)


@router.get(
    "/updates",
    summary="Per-update analytics (Admin only)",
    description="Returns view count, reaction count, and reaction breakdown for each published changelog.",
)
async def analytics_updates(
    limit: int = Query(default=20, ge=1, le=100),
    admin_user: UserModel = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await analytics_service.get_update_performance(db, limit=limit)


@router.post(
    "/view/{changelog_id}",
    summary="Record a changelog view (Public)",
    description="Records an anonymous view event for a changelog. Uses a salted hash of IP+UA. Deduplicates within a 1-hour cooldown per visitor per changelog.",
)
async def record_view(
    changelog_id: str,
    request: Request,
    current_user: UserModel | None = Depends(get_optional_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = str(current_user.id) if current_user else None
    recorded = await analytics_service.record_view(db, changelog_id, request, user_id)
    return {"recorded": recorded}
