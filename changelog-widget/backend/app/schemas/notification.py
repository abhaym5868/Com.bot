"""
schemas/notification.py
-----------------------
Pydantic schemas for the What's New Notification Center.
"""

from datetime import datetime
from pydantic import BaseModel
from app.schemas.changelog import ChangelogResponse


class NotificationCenterResponse(BaseModel):
    unread_count: int
    last_viewed_changelog_date: datetime | None = None
    recent_updates: list[ChangelogResponse]


class MarkReadResponse(BaseModel):
    unread_count: int = 0
    last_viewed_changelog_date: datetime
    message: str = "Notifications marked as read."
