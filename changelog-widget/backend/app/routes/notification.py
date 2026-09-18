"""
routes/notification.py
----------------------
API routes for What's New Notification Center:
- GET /api/v1/notifications
- POST /api/v1/notifications/mark-read
"""

from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.middleware.auth import get_current_user, get_optional_current_user
from app.models.user import UserModel
from app.schemas.notification import NotificationCenterResponse, MarkReadResponse
from app.services import notification_service

router = APIRouter()


@router.get(
    "",
    response_model=NotificationCenterResponse,
    summary="Get unread count and recent changelog updates",
    description="Calculates unread count based on user's last_viewed_changelog_date and returns recent published updates.",
)
async def get_notifications(
    limit: int = Query(default=5, ge=1, le=50, description="Number of recent updates to retrieve"),
    current_user: UserModel | None = Depends(get_optional_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = current_user.id if current_user else None
    return await notification_service.get_notification_center(db, user_id=user_id, limit=limit)


@router.post(
    "/mark-read",
    response_model=MarkReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notifications as read (Authenticated)",
    description="Updates user's last_viewed_changelog_date to current timestamp, resetting unread count to 0.",
)
async def mark_as_read(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await notification_service.mark_notifications_read(db, current_user.id)


@router.post(
    "/read",
    response_model=MarkReadResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def mark_as_read_alias(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await notification_service.mark_notifications_read(db, current_user.id)
