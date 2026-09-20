"""
models/view.py
--------------
View tracking document model for MongoDB.
Tracks anonymous page views per changelog without storing personal data.
"""

from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId, utc_now


class ViewModel(MongoBaseModel):
    """
    MongoDB representation of a changelog view event in the 'views' collection.
    Uses a salted visitor hash (IP + user-agent hash) instead of raw personal data.
    """
    changelog_id: PyObjectId = Field(..., description="ID of the viewed changelog")
    visitor_hash: str = Field(..., description="Anonymous visitor fingerprint (salted hash)")
    user_id: PyObjectId | None = Field(default=None, description="User ID if authenticated, else None")
    timestamp: datetime = Field(default_factory=utc_now)
