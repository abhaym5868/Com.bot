"""
services/notification_service.py
--------------------------------
Business logic for What's New Notification Center:
- Calculate unread published changelogs based on user's last_viewed_changelog_date
- Fetch recent published updates for the slide-over drawer
- Mark notifications as read by updating last_viewed_changelog_date to current timestamp
"""

import logging
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.base import utc_now
from app.models.changelog import ChangelogModel
from app.models.enums import ChangelogStatus
from app.schemas.changelog import ChangelogResponse
from app.schemas.notification import NotificationCenterResponse, MarkReadResponse

logger = logging.getLogger(__name__)


async def get_notification_center(
    db: AsyncIOMotorDatabase,
    user_id: str | None = None,
    limit: int = 5,
) -> NotificationCenterResponse:
    """
    Returns unread changelog count and recent published updates.
    If authenticated, unread_count is published posts with published_at > last_viewed_changelog_date.
    If unauthenticated, returns total recent updates with unread_count=0.
    """
    unread_count = 0
    last_viewed: None = None

    if user_id and ObjectId.is_valid(user_id):
        user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
        if user_doc:
            last_viewed = user_doc.get("last_viewed_changelog_date")
            unread_filter = {"status": ChangelogStatus.PUBLISHED.value}
            if last_viewed:
                unread_filter["published_at"] = {"$gt": last_viewed}
            unread_count = await db["changelogs"].count_documents(unread_filter)

    # Fetch recent published updates
    cursor = (
        db["changelogs"]
        .find({"status": ChangelogStatus.PUBLISHED.value})
        .sort([("published_at", -1), ("created_at", -1)])
        .limit(limit)
    )

    recent_updates: list[ChangelogResponse] = []
    async for doc in cursor:
        model = ChangelogModel(**doc)
        recent_updates.append(ChangelogResponse.model_validate(model.model_dump()))

    return NotificationCenterResponse(
        unread_count=unread_count,
        last_viewed_changelog_date=last_viewed,
        recent_updates=recent_updates,
    )


async def mark_notifications_read(
    db: AsyncIOMotorDatabase,
    user_id: str,
) -> MarkReadResponse:
    """
    Updates the user's last_viewed_changelog_date to the current UTC timestamp,
    immediately resetting unread count to 0.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format.",
        )

    now = utc_now()
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"last_viewed_changelog_date": now, "updated_at": now}},
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return MarkReadResponse(
        unread_count=0,
        last_viewed_changelog_date=now,
        message="Notifications marked as read.",
    )
